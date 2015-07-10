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

#include <iostream>
#include <memory>
#include <string>

#include <grpc/grpc.h>
#include <grpc++/server.h>
#include <grpc++/server_builder.h>
#include <grpc++/server_context.h>
#include <grpc++/server_credentials.h>
#include <grpc++/status.h>
#include "perf_db.grpc.pb.h"
#include "database_manager.h"
#include <cstdlib>
#include <gflags/gflags.h>

DEFINE_string(perf_server_addr, "", "Address of server in Hostname:Port format");
DEFINE_string(database, "", "Location of the metrics database");
DEFINE_string(auth_server_addr, "", "Address of the authentication server");
// In some distros, gflags is in the namespace google, and in some others,
// in gflags. This hack is enabling us to find both.
namespace google {}
namespace gflags {}
using namespace google;
using namespace gflags;

namespace grpc{
namespace testing{

class PerfDbTransferServiceImpl final : public PerfDbTransfer::Service {
public:
  PerfDbTransferServiceImpl() {
    //Set and initialize database
    db_manager.setDatabase(FLAGS_database);
    db_manager.setAuthServerAddress(FLAGS_auth_server_addr);
  }

  Status RecordSingleClientData(ServerContext* context, const SingleUserRecordRequest* request,
                  SingleUserRecordReply* reply) override {
    //record single user's data to database
    bool result = db_manager.recordSingleUserData(request);
    
    if(result) {
      return Status::OK;
    }
    else {
      return Status::Cancelled;
    }
  }

  Status RetrieveSingleUserData(ServerContext* context, const SingleUserRetrieveRequest* request,
                  SingleUserRetrieveReply* reply) override {
    //retrieve single user's records from database                   
    *reply = db_manager.retrieveSingleUserData(request);
    return Status::OK;
  }

  Status RetrieveAllUsersData(ServerContext* context, const AllUsersRetrieveRequest* request,
                  AllUsersRetrieveReply* reply) override {
    //retrieve all users' records from database
    *reply = db_manager.retrieveAllUsersData(request);
    return Status::OK;
  }
private:
  DatabaseManager db_manager;
};

void RunServer() {
  PerfDbTransferServiceImpl service;
  ServerBuilder builder;

  //Terminate if address not provided
  if(FLAGS_perf_server_addr.empty()) {
    std::cout << "No address provided. Terminating.\n";
    exit(1);
  }

  builder.AddListeningPort(FLAGS_perf_server_addr, grpc::InsecureServerCredentials());
  builder.RegisterService(&service);
  std::unique_ptr<Server> server(builder.BuildAndStart());
  std::cout << "Server listening on " << FLAGS_perf_server_addr << std::endl;
  server->Wait();
}

} //testing
} //grpc

int main(int argc, char** argv) {
  google::ParseCommandLineFlags(&argc, &argv, true);
  grpc::testing::RunServer();

  return 0;
}
