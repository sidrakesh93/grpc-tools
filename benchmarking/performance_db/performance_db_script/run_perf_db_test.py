#!/usr/bin/python
#
# Copyright 2015, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import os
import sys
import argparse
from oauth2client import tools
from oauth2client import client
from oauth2client.file import Storage
from apiclient.discovery import build
import httplib2
import subprocess
import hashlib
import auth_user_pb2
import re

parser = argparse.ArgumentParser(description='Report metrics to performance database', parents=[tools.argparser])
parser.add_argument('--test', type=str, help='Name of the test to be executed')
parser.add_argument('--username', type=str, help='Gmail address of the user')
parser.add_argument('--data_server_address', type=str, default='0.0.0.0:50052', help='Address of the performance database server')
parser.add_argument('--auth_server_address', type=str, default='0.0.0.0:2817', help='Address of the authentication server')
parser.add_argument('--creds_dir', type=str, default=os.path.expanduser('~')+'/.grpc/credentials', help='Path to the access tokens directory')
parser.add_argument('--client_secrets', type=str, default=os.path.expanduser('~')+'/.grpc/credentials/client_secrets.json')
parser.add_argument('--tag', type=str, default='', help='Tag for the test')

def authenticateUser(username, creds_dir, server_address, client_secrets, args):
  user_creds_file = creds_dir + '/' + username
  storage = Storage(user_creds_file)

  if(not os.path.exists(user_creds_file)):
    flow = client.flow_from_clientsecrets(client_secrets, scope='email profile', redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    credentials = tools.run_flow(flow, storage, args)
  else:
    credentials = storage.get()

  address_port = server_address.split(':')

  with auth_user_pb2.early_adopter_create_Authentication_stub(address_port[0], int(address_port[1])) as stub:
    authenticate_user_request = auth_user_pb2.AuthenticateUserRequest()
    authenticate_user_request.credentials = open(user_creds_file, "rb").read()
    authenticate_user_request.username = username

    _TIMEOUT_SECONDS = 10 # Max waiting time before timeout, in seconds

    reply_future = stub.AuthenticateUser.async(authenticate_user_request, _TIMEOUT_SECONDS)
    reply = reply_future.result()

  http_auth = credentials.authorize(httplib2.Http())
  auth_service = build('oauth2', 'v2', http=http_auth)

  user_info = auth_service.userinfo().get().execute()
  hash_object = hashlib.md5(user_info.get('id'))
  
  return hash_object.hexdigest()

def getSysInfo():
  # Fetch system information
  sysInfo = os.popen('lscpu').readlines()

  NICs = os.popen('ifconfig | cut -c1-8 | sed \'/^\s*$/d\' | sort -u').readlines()
  nicAddrs = os.popen('ifconfig | grep -oE "inet addr:([0-9]{1,3}\.){3}[0-9]{1,3}"').readlines()

  nicInfo = []

  for i in range(0, len(NICs)):
    NIC = NICs[i]
    NIC = re.sub(r'[^\w]', '', NIC)

    ethtoolProcess = subprocess.Popen(["ethtool",NIC], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ethtoolResult = ethtoolProcess.communicate()[0]

    ethtoolResultList = ethtoolResult.split('\n\t')
    for ethtoolString in ethtoolResultList:
      if ethtoolString.startswith('Speed'):
        ethtoolString = ethtoolString.split(':')[1]
        ethtoolString = ethtoolString.replace('Mb/s',' Mbps')
        nicInfo.append('NIC ' + NIC + ' speed: ' + ethtoolString + '\n')
        nicInfo.append(NIC + ' inet address: ' + nicAddrs[i].split(':')[1])

  print 'Obtaining network info....'
  tcp_rr_rate = str(os.popen('netperf -t TCP_RR -v 0').readlines()[1])
  print 'Network info obtained'
  
  nicInfo.append('TCP RR transmission rate per sec: ' + tcp_rr_rate + '\n')
  sysInfo = sysInfo + nicInfo

  return sysInfo

def main(argv):
  args = parser.parse_args()

  creds_dir = args.creds_dir
  data_server_address = args.data_server_address
  auth_server_address = args.auth_server_address
  client_secrets = args.client_secrets
  # Fetch working access token
  hashed_id = authenticateUser(args.username, creds_dir, auth_server_address, client_secrets, args)

  # Get path to test
  test_path = args.test

  # Get name of the test
  try:
    test_name = test_path.split('/')[-1]
  except AttributeError:
    print '\nError: Please provide test name/path as argument\n'
    sys.exit(1)

  # Get the system information
  sys_info = getSysInfo()

  tag = args.tag

  try:
    print '\nBeginning test:\n'
    # Run the test
    subprocess.call([test_path, '--report_metrics_db=true', '--hashed_id='+hashed_id, '--test_name='+test_name, 
      '--sys_info='+str(sys_info).strip('[]'), '--server_address='+data_server_address, '--tag='+tag])
  except OSError:
    print 'Could not execute the test'

if __name__ == "__main__":
  main(sys.argv)
