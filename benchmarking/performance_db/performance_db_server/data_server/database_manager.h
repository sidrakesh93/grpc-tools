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

#include <string>
#include "leveldb/db.h"
#include "leveldb/cache.h"
#include "perf_db.grpc.pb.h"
#include "auth_user.grpc.pb.h"
#include <curl/curl.h>
#include <grpc++/channel_arguments.h>
#include <grpc++/client_context.h>
#include <grpc++/create_channel.h>

namespace grpc{
namespace testing{

//Class to interact with the database
class DatabaseManager{
  public:
    DatabaseManager();
    ~DatabaseManager();

    void setAuthServerAddress(std::string auth_server_address);

    //To set and initialize database
    void setDatabase(std::string database);
    
    //To record a single user's record
    bool recordSingleUserData(const SingleUserRecordRequest* request);
    
    //To retrieve a single user's records
    SingleUserRetrieveReply retrieveSingleUserData(const SingleUserRetrieveRequest* request);
    
    //To retrieve all user's records
    AllUsersRetrieveReply retrieveAllUsersData(const AllUsersRetrieveRequest* request);
    
  private:
    leveldb::DB* db = 0;  //database pointer
    std::string database_;  //database name
    std::string auth_server_address_;
    std::unique_ptr<leveldb::Cache> memory_cache_;  //memory cache
    
    //Returns current datetime string
    const std::string currentDateTime();
    
    //Clears sensitive fields from stored data before sending
    void clearAddressFields(SingleUserDetails* single_user_details);
};

}  //testing
}  //grpc
