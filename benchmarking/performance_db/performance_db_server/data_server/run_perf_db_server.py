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
"""This script runs the performance database server."""

import argparse
import os
import subprocess

parser = argparse.ArgumentParser(description='Run performance database server')

parser.add_argument('--bin',
                    type=str,
                    default='../../bins/perf_db_server',
                    help='Location of the performance database server binary')
parser.add_argument('--perf_server_addr',
                    type=str,
                    default='0.0.0.0:50052',
                    help='Address for performance database server')
parser.add_argument('--database',
                    type=str,
                    default=os.path.expanduser('~/.grpc/perf_db'),
                    help='Location of performance database')
parser.add_argument('--auth_server_addr',
                    type=str,
                    default='0.0.0.0:2817',
                    help='Address of authentication server')


def main():
  args = parser.parse_args()

  if not os.path.exists(args.database):
    os.makedirs(args.database)

  try:
    # Run the test
    subprocess.call([args.bin, '--perf_server_addr=' + args.perf_server_addr,
                     '--database=' + args.database,
                     '--auth_server_addr=' + args.auth_server_addr])
  except OSError, e:
    print e, 'Could not execute server'


if __name__ == '__main__':
  main()
