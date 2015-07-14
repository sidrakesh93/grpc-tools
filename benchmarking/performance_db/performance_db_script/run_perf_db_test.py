#!/usr/bin/python
#
# Copyright 2015 Google Inc. All Rights Reserved.
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

import argparse
import hashlib
import os
import re
import subprocess
import sys
from apiclient import discovery
import httplib2
from oauth2client import client
from oauth2client import tools
from oauth2client import file
import auth_user_pb2

parser = argparse.ArgumentParser(
    description='Report metrics to performance database',
    parents=[tools.argparser])
parser.add_argument('--test', type=str, help='Name of the test to be executed')
parser.add_argument('--username', type=str, help='Username')
parser.add_argument('--data_server_addr',
                    type=str,
                    default='0.0.0.0:50052',
                    help='Address of the performance database server')
parser.add_argument('--auth_server_addr',
                    type=str,
                    default='0.0.0.0:2817',
                    help='Address of the authentication server')
parser.add_argument('--creds_dir',
                    type=str,
                    default=os.path.expanduser('~/.grpc/credentials'),
                    help='Path to the access tokens directory')
parser.add_argument('--client_secrets',
                    type=str,
                    default='client_secrets.json',
                    help='Location of the client_secrets.json file')
parser.add_argument('--tag', type=str, default='', help='Tag for the test')

REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
SCOPE = 'email profile'


def auth_user(username, creds_dir, auth_server_addr, client_secrets, args):
  """Performs authentication for the user."""
  if not os.path.exists(creds_dir):
    os.makedirs(creds_dir)

  user_creds_file = creds_dir + '/' + username
  storage = file.Storage(user_creds_file)

  # Acquire user credentials if not already stored, else re-use
  if not os.path.exists(user_creds_file):
    flow = client.flow_from_clientsecrets(client_secrets,
                                          scope=SCOPE,
                                          redirect_uri=REDIRECT_URI)
    credentials = tools.run_flow(flow, storage, args)
  else:
    credentials = storage.get()

  # Split the addr and port
  addr_port = auth_server_addr.split(':')

  # Request authentication from authentication server
  with auth_user_pb2.early_adopter_create_Authentication_stub(
      addr_port[0], int(addr_port[1])) as stub:
    auth_user_request = auth_user_pb2.AuthenticateUserRequest()
    auth_user_request.credentials = open(user_creds_file, 'rb').read()
    auth_user_request.username = username

    timeout_secs = 10  # Max waiting time before timeout, in seconds

    auth_user_reply_future = stub.AuthenticateUser.async(auth_user_request,
                                                         timeout_secs)
    auth_user_reply = auth_user_reply_future.result()

    # If requested username not unique, send request again with new username
    while auth_user_reply.is_unique_username != True:
      username = raw_input('\nUsername already taken, please enter a new one: ')
      auth_user_request.username = username
      auth_user_reply_future = stub.AuthenticateUser.async(auth_user_request,
                                                           timeout_secs)
      auth_user_reply = auth_user_reply_future.result()

  # Return hashed user id
  http_auth = credentials.authorize(httplib2.Http())
  auth_service = discovery.build('oauth2', 'v2', http=http_auth)

  user_info = auth_service.userinfo().get().execute()
  hash_object = hashlib.md5(user_info.get('id'))

  return hash_object.hexdigest()


def get_sys_info():
  """Fetches system information."""
  sys_info = os.popen('lscpu').readlines()

  nics = os.popen(
      'ifconfig | cut -c1-8 | sed \'/^\s*$/d\' | sort -u').readlines()
  nic_addrs = os.popen(
      'ifconfig | grep -oE "inet addr:([0-9]{1,3}\.){3}[0-9]{1,3}"').readlines()

  nic_info = []

  for i in range(0, len(nics)):
    nic = nics[i]
    nic = re.sub(r'[^\w]', '', nic)

    ethtool_process = subprocess.Popen(['ethtool', nic],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    ethtool_result = ethtool_process.communicate()[0]

    ethtool_result_list = ethtool_result.split('\n\t')
    for ethtool_str in ethtool_result_list:
      if ethtool_str.startswith('Speed'):
        ethtool_str = ethtool_str.split(':')[1]
        nic_info.append('NIC ' + nic + ' speed: ' + ethtool_str + '\n')
        nic_info.append(nic + ' inet addr: ' + nic_addrs[i].split(':')[1])

  print 'Obtaining network info....'
  tcp_rr_rate = str(os.popen('netperf -t TCP_RR -v 0').readlines()[1])
  print 'Network info obtained'

  nic_info.append('TCP RR transmission rate per sec: ' + tcp_rr_rate + '\n')
  sys_info += nic_info

  return sys_info


def main():
  args = parser.parse_args()

  creds_dir = args.creds_dir
  data_server_addr = args.data_server_addr
  auth_server_addr = args.auth_server_addr
  client_secrets = args.client_secrets
  # Fetch working access token
  hashed_id = auth_user(args.username, creds_dir, auth_server_addr,
                        client_secrets, args)

  # Get path to test
  test_path = args.test

  if test_path == None:
    print '\nError: Please provide test name/path as argument\n'
    sys.exit(1)

  test_name = test_path.split('/')[-1]

  # Get the system information
  sys_info = get_sys_info()

  tag = args.tag

  try:
    print '\nBeginning test:\n'
    # Run the test
    subprocess.call([
        test_path, '--report_metrics_db=true', '--hashed_id=' + hashed_id,
        '--test_name=' + test_name, '--sys_info=' + str(sys_info).strip('[]'),
        '--server_address=' + data_server_addr, '--tag=' + tag
    ])
  except OSError:
    print 'Could not execute the test'


if __name__ == '__main__':
  main()
