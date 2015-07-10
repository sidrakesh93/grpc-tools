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

namespace grpc {
namespace testing {

DatabaseManager::DatabaseManager() {}

DatabaseManager::~DatabaseManager() {
  // delete database pointer
  delete db;
}

void DatabaseManager::setAuthServerAddress(std::string auth_server_address) {
  auth_server_address_ = auth_server_address;
}

void DatabaseManager::setDatabase(std::string database) {
  database_ = database;

  // set databse options
  leveldb::Options options;
  options.block_cache = leveldb::NewLRUCache(100 * 1048576);  // caching data
  options.create_if_missing = true;

  leveldb::Status status = leveldb::DB::Open(options, database_, &db);
  assert(status.ok());
}

// Get current date/time, format is YYYY-MM-DD.HH:mm:ss
const std::string DatabaseManager::currentDateTime() {
  time_t now = time(0);
  struct tm tstruct;
  char buf[80];
  tstruct = *localtime(&now);

  strftime(buf, sizeof(buf), "%FT%XZ", &tstruct);
  return buf;
}

// To record a single user's record
bool DatabaseManager::recordSingleUserData(
    const SingleUserRecordRequest* request) {
  // Obtain user details
  std::unique_ptr<Authentication::Stub> stub_ =
      Authentication::NewStub(grpc::CreateChannel(
          auth_server_address_, grpc::InsecureCredentials(), ChannelArguments()));

  ClientContext context;

  ConfirmUserRequest confirm_user_request;
  confirm_user_request.set_hashed_id(request->hashed_id());

  ConfirmUserReply confirm_user_reply;

  Status user_status = stub_->ConfirmUser(&context, confirm_user_request, &confirm_user_reply);

  if(!confirm_user_reply.is_authenticated()) {
    return false;
  }

  string prev_value;
  // get existing user details from database, using user id as key
  leveldb::Status status =
      db->Get(leveldb::ReadOptions(), request->hashed_id(), &prev_value);

  SingleUserDetails single_user_details;

  if (status.ok()) {
    single_user_details.ParseFromString(prev_value);
  }

  single_user_details.set_username(confirm_user_reply.username());
  single_user_details.set_hashed_id(request->hashed_id());

  // Add new record details
  DataDetails* data_details = single_user_details.add_data_details();

  data_details->set_timestamp(currentDateTime());
  data_details->set_test_name(request->test_name());
  data_details->set_sys_info(request->sys_info());
  data_details->set_tag(request->tag());

  *(data_details->mutable_metrics()) = request->metrics();
  *(data_details->mutable_client_config()) = request->client_config();
  *(data_details->mutable_server_config()) = request->server_config();

  string new_value;
  single_user_details.SerializeToString(&new_value);

  // write back to database
  status = db->Put(leveldb::WriteOptions(), request->hashed_id(), new_value);
  assert(status.ok());

  return true;
}

// To retrieve a single user's records
SingleUserRetrieveReply DatabaseManager::retrieveSingleUserData(
    const SingleUserRetrieveRequest* request) {
  // Get stored data
  string value;
  leveldb::Status status =
      db->Get(leveldb::ReadOptions(), request->user_id(), &value);

  SingleUserRetrieveReply single_user_retrieve_reply;
  SingleUserDetails* single_user_details =
      single_user_retrieve_reply.mutable_single_user_data();

  if (status.ok()) {
    single_user_details->ParseFromString(value);
  }

  // remove senstive information
  clearAddressFields(single_user_details);

  return single_user_retrieve_reply;
}

// To retrieve all user's records
AllUsersRetrieveReply DatabaseManager::retrieveAllUsersData(
    const AllUsersRetrieveRequest* request) {
  leveldb::ReadOptions options;

  // Create snapshot to provide consistent read-only views over the entire state
  // of the database
  options.snapshot = db->GetSnapshot();

  leveldb::Iterator* it = db->NewIterator(options);

  AllUsersRetrieveReply all_users_retrieve_reply;

  // Iterate over all the stored data and remove all sensitive data
  for (it->SeekToFirst(); it->Valid(); it->Next()) {
    SingleUserDetails* single_user_details =
        all_users_retrieve_reply.add_all_users_data();
    single_user_details->ParseFromString(it->value().ToString());

    clearAddressFields(single_user_details);
  }

  assert(it->status().ok());  // Check for any errors found during the scan
  delete it;

  db->ReleaseSnapshot(options.snapshot);

  return all_users_retrieve_reply;
}

// Removes Inet address from sys info string and returns modified string
string removeInetAddrs(string sys_info) {
  string new_sys_info = "";

  size_t pos = 0;
  std::string token;

  while ((pos = sys_info.find(",")) != std::string::npos) {
    token = sys_info.substr(0, pos);

    // If not inet address, add back to original list
    if (token.find("inet address") == std::string::npos) {
      new_sys_info += token + ",";
    }

    sys_info.erase(0, pos + 1);
  }

  new_sys_info += sys_info;
  return new_sys_info;
}

// Clears sensitive fields from stored data before sending
void DatabaseManager::clearAddressFields(SingleUserDetails* single_user_details) {
  for (int i = 0; i < single_user_details->data_details_size(); i++) {
    DataDetails* data_details = single_user_details->mutable_data_details(i);
    ClientConfig* client_config = data_details->mutable_client_config();
    ServerConfig* server_config = data_details->mutable_server_config();

    // Remove Inet addresses from the sys info stirng
    string sys_info = data_details->sys_info();
    data_details->set_sys_info(removeInetAddrs(sys_info));

    // Remove server targets and host from client config
    auto client_reflection = client_config->GetReflection();
    auto client_descriptor = client_config->GetDescriptor();

    auto server_targets_descriptor =
        client_descriptor->FindFieldByName("server_targets");
    auto client_host_descriptor = client_descriptor->FindFieldByName("host");

    client_reflection->ClearField(client_config, server_targets_descriptor);
    client_reflection->ClearField(client_config, client_host_descriptor);

    // Remove host from server config
    auto server_reflection = server_config->GetReflection();
    auto server_descriptor = server_config->GetDescriptor();

    auto server_host_descriptor = server_descriptor->FindFieldByName("host");

    server_reflection->ClearField(server_config, server_host_descriptor);
  }
}
}
}
