/*
 *
 * Copyright 2015, Google Inc.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 *     * Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above
 * copyright notice, this list of conditions and the following disclaimer
 * in the documentation and/or other materials provided with the
 * distribution.
 *     * Neither the name of Google Inc. nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

#include "database_manager.h"
#include <ctime>
#include <cassert>
#include <fstream>

#define USER_INFO_URL "https://www.googleapis.com/oauth2/v1/userinfo?access_token="

namespace grpc{
namespace testing{

DatabaseManager::DatabaseManager() {}

DatabaseManager::~DatabaseManager() {
  //delete database pointer
  delete db;
}

void DatabaseManager::setDatabase(std::string database) {
  database_ = database;
  
  //set databse options
  leveldb::Options options;
  options.block_cache = leveldb::NewLRUCache(100 * 1048576);  //caching data
  options.create_if_missing = true;
  
  leveldb::Status status = leveldb::DB::Open(options, database_, &db);
  assert(status.ok());
}

//Get current date/time, format is YYYY-MM-DD.HH:mm:ss
const std::string DatabaseManager::currentDateTime() {
  time_t     now = time(0);
  struct tm  tstruct;
  char       buf[80];
  tstruct = *localtime(&now);

  strftime(buf, sizeof(buf), "%m/%d/%Y, %X", &tstruct);
  return buf;
}

//Helper function for using libcurl
static size_t WriteCallback(void *contents, size_t size, size_t nmemb, void *userp) {
  ((string*)userp)->append((char*)contents, size * nmemb);
  return size * nmemb;
}

//Libcurl used to get user details data
UserDetails DatabaseManager::getUserData(std::string accessToken) {
  string url = USER_INFO_URL + accessToken; //query url
  CURL *curl;
  CURLcode res;
  string readBuffer;

  UserDetails userDetails;

  curl = curl_easy_init();
  if(curl) {
    //Get data
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
    res = curl_easy_perform(curl);
    curl_easy_cleanup(curl);

    std::string err;
    //Write received JSON data to user details protobuf
    int ret = pbjson::json2pb(readBuffer, &userDetails, err);
  }

  return userDetails;
}

void DatabaseManager::recordSingleUserData(const SingleUserRecordRequest* request) {
  //Obtain user details
  UserDetails userDetails = getUserData(request->access_token());

  string prevValue;
  //get existing user details from database, using user id as key
  leveldb::Status status = db->Get(leveldb::ReadOptions(), userDetails.id(), &prevValue);

  SingleUserDetails singleUserDetails;
  
  if(status.ok())
    singleUserDetails.ParseFromString(prevValue);

  //Add new record details
  DataDetails* dataDetails = singleUserDetails.add_data_details();

  dataDetails->set_timestamp(currentDateTime());
  dataDetails->set_test_name(request->test_name());
  dataDetails->set_sys_info(request->sys_info());
  
  *(dataDetails->mutable_metrics()) = request->metrics();
  *(dataDetails->mutable_client_config()) = request->client_config();
  *(dataDetails->mutable_server_config()) = request->server_config();
  *(singleUserDetails.mutable_user_details()) = userDetails;

  string newValue;
  singleUserDetails.SerializeToString(&newValue);

  //write back to database
  status = db->Put(leveldb::WriteOptions(), userDetails.id(), newValue);
  assert(status.ok());
}

SingleUserRetrieveReply DatabaseManager::retrieveSingleUserData(const SingleUserRetrieveRequest* request) {
  string value;
  leveldb::Status status  = db->Get(leveldb::ReadOptions(), request->user_id(), &value); 

  SingleUserRetrieveReply singleUserRetrieveReply;
  SingleUserDetails* singleUserDetails = singleUserRetrieveReply.mutable_details();

  if(status.ok())
    singleUserDetails->ParseFromString(value);

  clearAddressFields(singleUserDetails);

  return singleUserRetrieveReply;
}

AllUsersRetrieveReply DatabaseManager::retrieveAllUsersData(const AllUsersRetrieveRequest* request) {
  leveldb::ReadOptions options;
  options.snapshot = db->GetSnapshot();

  leveldb::Iterator* it = db->NewIterator(options);

  AllUsersRetrieveReply allUsersRetrieveReply;

  for (it->SeekToFirst(); it->Valid(); it->Next()) {
    SingleUserDetails* singleUserDetails = allUsersRetrieveReply.add_user_data();
    singleUserDetails->ParseFromString(it->value().ToString());

    clearAddressFields(singleUserDetails);
  }

  assert(it->status().ok());  // Check for any errors found during the scan
  delete it;

  db->ReleaseSnapshot(options.snapshot);

  return allUsersRetrieveReply;
}

string removeInetAddrs(string sysInfo) {
  string newSysInfo = "";

  size_t pos = 0;
  std::string token;
  
  while ((pos = sysInfo.find(",")) != std::string::npos) {
    token = sysInfo.substr(0, pos);

    //If not inet address, add back to original list
    if(token.find("inet address") == std::string::npos) {
      newSysInfo += token + ",";
    }

    sysInfo.erase(0, pos + 1);
  }
  
  newSysInfo += sysInfo;
  return newSysInfo;
}

void DatabaseManager::clearAddressFields(SingleUserDetails* singleUserDetails) {
  for(int i=0; i < singleUserDetails->data_details_size(); i++) {
    
    DataDetails* dataDetails = singleUserDetails->mutable_data_details(i);
    ClientConfig* clientConfig = dataDetails->mutable_client_config();
    ServerConfig* serverConfig = dataDetails->mutable_server_config();
    
    string sysInfo = dataDetails->sys_info();
    dataDetails->set_sys_info(removeInetAddrs(sysInfo));

    auto clientReflection = clientConfig->GetReflection();
    auto clientDescriptor = clientConfig->GetDescriptor();

    auto serverTargetsDescriptor = clientDescriptor->FindFieldByName("server_targets");
    auto clientHostDescriptor = clientDescriptor->FindFieldByName("host");

    clientReflection->ClearField(clientConfig, serverTargetsDescriptor);
    clientReflection->ClearField(clientConfig, clientHostDescriptor);

    auto serverReflection = serverConfig->GetReflection();
    auto serverDescriptor = serverConfig->GetDescriptor();

    auto serverHostDescriptor = serverDescriptor->FindFieldByName("host");

    serverReflection->ClearField(serverConfig, serverHostDescriptor);
  }
}

}
}