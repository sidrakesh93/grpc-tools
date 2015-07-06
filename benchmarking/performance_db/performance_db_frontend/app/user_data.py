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
#!/usr/bin/python

import perf_db_pb2
import qpstest_pb2
import re
from collections import defaultdict
from django.conf import settings

# Class to communicate with performance database server
class UserData(object):

  def __init__(self):
    # Set hostname and port
    self.hostname = settings.PERF_DB_HOSTNAME
    self.port = settings.PERF_DB_PORT

  # Returns a dictionary of parsed time
  def parseTimeString(self, timeString):
    parsed_time_list = re.split('\W+', timeString)
    parsed = {}
    parsed['month'] = parsed_time_list[0]
    parsed['day'] = parsed_time_list[1]
    parsed['year'] = parsed_time_list[2]
    parsed['hour'] = parsed_time_list[3]
    parsed['min'] = parsed_time_list[4]
    parsed['sec'] = parsed_time_list[5]
    return parsed

  # Initialize a single metric record dictionary
  def initSingleDataDict(self, testName, timestamp, client_config, server_config, sys_info, tag):
    single_data_dict = {}
    single_data_dict['test_name'] = testName;
    single_data_dict['timestamp'] = self.parseTimeString(timestamp)
    single_data_dict['client_config'] = self.getClientConfigDict(client_config)
    single_data_dict['server_config'] = self.getServerConfigDict(server_config)
    single_data_dict['sys_info'] = self.getSysInfoDict(sys_info)
    single_data_dict['tag'] = tag

    return single_data_dict

  # Returns a single user's data
  def getSingleUserData(self, user_id):
    # Create Stub to communicate with performance database server
    with perf_db_pb2.early_adopter_create_PerfDbTransfer_stub(self.hostname, self.port) as stub:
      single_user_retrieve_request = perf_db_pb2.SingleUserRetrieveRequest()
      single_user_retrieve_request.user_id = user_id
      
      _TIMEOUT_SECONDS = 10 # Max waiting time before timeout, in seconds

      # Request data and receive data from performance database server asynchronously
      user_data_future = stub.RetrieveSingleUserData.async(single_user_retrieve_request, _TIMEOUT_SECONDS)
      user_data = user_data_future.result()

      # Sort the data
      sorted_user_data = sorted(user_data.single_user_data.data_details, key=lambda data_detail: data_detail.timestamp)

      # Lists for various metrics
      qps_list = []
      qps_per_core_list = []
      lat_list = []
      times_list = []

      for data_detail in sorted_user_data:
        if data_detail.metrics.qps != 0.0: # qps present
          single_data_dict = self.initSingleDataDict(data_detail.test_name, data_detail.timestamp, data_detail.client_config, data_detail.server_config, data_detail.sys_info, data_detail.tag)
          single_data_dict['qps'] = round(data_detail.metrics.qps,1)
          qps_list.append(single_data_dict)

        if data_detail.metrics.qps_per_core != 0.0: # qps per core present
          single_data_dict = self.initSingleDataDict(data_detail.test_name, data_detail.timestamp, data_detail.client_config, data_detail.server_config, data_detail.sys_info, data_detail.tag)
          single_data_dict['qps_per_core'] = round(data_detail.metrics.qps_per_core,1)
          qps_per_core_list.append(single_data_dict)
        
        if data_detail.metrics.perc_lat_50 != 0.0 and data_detail.metrics.perc_lat_90 != 0.0 and data_detail.metrics.perc_lat_95 != 0.0 and data_detail.metrics.perc_lat_99 != 0.0 and data_detail.metrics.perc_lat_99_point_9 != 0.0: # percentile latenices present
          single_data_dict = self.initSingleDataDict(data_detail.test_name, data_detail.timestamp, data_detail.client_config, data_detail.server_config, data_detail.sys_info, data_detail.tag)
          
          lat_dict = {}
          lat_dict['perc_lat_50'] = round(data_detail.metrics.perc_lat_50,1)
          lat_dict['perc_lat_90'] = round(data_detail.metrics.perc_lat_90,1)
          lat_dict['perc_lat_95'] = round(data_detail.metrics.perc_lat_95,1)
          lat_dict['perc_lat_99'] = round(data_detail.metrics.perc_lat_99,1)
          lat_dict['perc_lat_99_point_9'] = round(data_detail.metrics.perc_lat_99_point_9,1)

          single_data_dict['lat'] = lat_dict
          lat_list.append(single_data_dict)
        
        if data_detail.metrics.server_system_time != 0.0 and data_detail.metrics.server_user_time != 0.0 and data_detail.metrics.client_system_time != 0.0 and data_detail.metrics.client_user_time != 0.0: # Server and client times present
          single_data_dict = self.initSingleDataDict(data_detail.test_name, data_detail.timestamp, data_detail.client_config, data_detail.server_config, data_detail.sys_info, data_detail.tag)

          times_dict = {}
          times_dict['server_system_time'] = round(data_detail.metrics.server_system_time,1)
          times_dict['server_user_time'] = round(data_detail.metrics.server_user_time,1)
          times_dict['client_system_time'] = round(data_detail.metrics.client_system_time,1)
          times_dict['client_user_time'] = round(data_detail.metrics.client_user_time,1)
          
          single_data_dict['times'] = times_dict
          times_list.append(single_data_dict)

      data_dict = defaultdict(list)
      data_dict['qpsData'] = qps_list
      data_dict['qpsPerCoreData'] = qps_per_core_list
      data_dict['latData'] = lat_list
      data_dict['timesData'] = times_list

      # Return user's personal details and user's data
      return [user_data.single_user_data.username, data_dict]

  # If non-zero value present, returns it
  def validValue(self, val):
    if val != 0.0:
      return round(val,1)
    else:
      return '-'

  # Returns server configuration dictionary
  def getServerConfigDict(self, server_config):
    server_config_dict = {}

    if server_config.server_type == qpstest_pb2.SYNCHRONOUS_SERVER:
      server_config_dict['Server Type'] = 'Synchronous'
    elif server_config.server_type == qpstest_pb2.ASYNC_SERVER:
      server_config_dict['Server Type'] = 'Asynchronous'

    server_config_dict['Threads'] = str(server_config.threads)
    server_config_dict['Enable SSL'] = str(server_config.enable_ssl)

    return server_config_dict

  # Returns client configuration dictionary
  def getClientConfigDict(self, client_config):
    client_config_dict = {}

    if client_config.client_type == qpstest_pb2.SYNCHRONOUS_CLIENT:
      client_config_dict['Client Type'] = 'Synchronous'
    elif client_config.client_type == qpstest_pb2.ASYNC_CLIENT:
      client_config_dict['Client Type'] = 'Asynchronous'
      client_config_dict['Asynchronous Client Threads'] = str(client_config.async_client_threads)

    client_config_dict['Outstanding RPCs Per Channel'] = str(client_config.outstanding_rpcs_per_channel)
    client_config_dict['Client Channels'] = str(client_config.client_channels)
    client_config_dict['Payload Size'] = str(client_config.payload_size)
    
    if client_config.rpc_type == qpstest_pb2.UNARY:
      client_config_dict['RPC Type'] = 'Unary'
    elif client_config.rpc_type == qpstest_pb2.STREAMING:
      client_config_dict['RPC Type'] = 'Streaming'

    client_config_dict['Enable SSL'] = str(client_config.enable_ssl)

    return client_config_dict

  # Returns system information dictionary
  def getSysInfoDict(self, sys_info):
    sys_info_dict = {}

    sys_info = sys_info.lstrip('\'')
    sys_info = sys_info.rstrip('\\n\'')

    sys_info_list = sys_info.split('\\n\', \'')

    for sys_info_str in sys_info_list:
      sys_info_param_list = re.split(':', sys_info_str)

      sys_param_value = sys_info_param_list[1].lstrip(' ')
      sys_info_dict[str(sys_info_param_list[0])] = str(sys_param_value)

    return sys_info_dict

  # Returns all the user's data for database table
  def getAllUsersData(self):
    metrics_table = []

    # Create Stub to communicate with performance database server
    with perf_db_pb2.early_adopter_create_PerfDbTransfer_stub(self.hostname, self.port) as stub:
      all_users_retrieve_request = perf_db_pb2.AllUsersRetrieveRequest()

      _TIMEOUT_SECONDS = 10 # Max waiting time before timeout, in seconds

      # Request data and receive data from performance database server asynchronously
      all_users_data_future = stub.RetrieveAllUsersData.async(all_users_retrieve_request, _TIMEOUT_SECONDS)
      all_users_data = all_users_data_future.result()

      for user_data in all_users_data.all_users_data:
        for data_detail in user_data.data_details:
          user_metrics_dict = {}
          user_metrics_dict['hashed_id'] = str(user_data.hashed_id)
          user_metrics_dict['username'] = str(user_data.username)
          user_metrics_dict['timestamp'] = self.parseTimeString(data_detail.timestamp)
          user_metrics_dict['test_name'] = str(data_detail.test_name)
          user_metrics_dict['qps'] = str(self.validValue(data_detail.metrics.qps))
          user_metrics_dict['qps_per_core'] = str(self.validValue(data_detail.metrics.qps_per_core))
          user_metrics_dict['perc_lat_50'] = str(self.validValue(data_detail.metrics.perc_lat_50))
          user_metrics_dict['perc_lat_90'] = str(self.validValue(data_detail.metrics.perc_lat_90))
          user_metrics_dict['perc_lat_95'] = str(self.validValue(data_detail.metrics.perc_lat_95))
          user_metrics_dict['perc_lat_99'] = str(self.validValue(data_detail.metrics.perc_lat_99))
          user_metrics_dict['perc_lat_99_point_9'] = str(self.validValue(data_detail.metrics.perc_lat_99_point_9))
          user_metrics_dict['server_system_time'] = str(self.validValue(data_detail.metrics.server_system_time))
          user_metrics_dict['server_user_time'] = str(self.validValue(data_detail.metrics.server_user_time))
          user_metrics_dict['client_system_time'] = str(self.validValue(data_detail.metrics.client_system_time))
          user_metrics_dict['client_user_time'] = str(self.validValue(data_detail.metrics.client_user_time))
          user_metrics_dict['server_config'] = self.getServerConfigDict(data_detail.server_config)
          user_metrics_dict['client_config'] = self.getClientConfigDict(data_detail.client_config)
          user_metrics_dict['sys_info'] = self.getSysInfoDict(data_detail.sys_info)
          user_metrics_dict['tag'] = str(data_detail.tag)

          metrics_table.append(user_metrics_dict)

    return metrics_table

  # Returns a particular metric data for all the users
  def getAllUsersSingleMetricData(self, metric):
    metricList = []

    # Create Stub to communicate with performance database server
    with perf_db_pb2.early_adopter_create_PerfDbTransfer_stub(self.hostname, self.port) as stub:
      all_users_retrieve_request = perf_db_pb2.AllUsersRetrieveRequest()

      _TIMEOUT_SECONDS = 10 # Max waiting time before timeout, in seconds

      # Request data and receive data from performance database server asynchronously
      all_users_data_future = stub.RetrieveAllUsersData.async(all_users_retrieve_request, _TIMEOUT_SECONDS)
      all_users_data = all_users_data_future.result()

      for user_data in all_users_data.all_users_data:
        for data_detail in user_data.data_details:
          user_metrics_dict = self.parseTimeString(data_detail.timestamp)

          if metric == 'QPS':
            user_metrics_dict['value'] = round(data_detail.metrics.qps,1)
          elif metric == 'qpsPerCore':
            user_metrics_dict['value'] = round(data_detail.metrics.qps_per_core,1)
          elif metric == 'p50':
            user_metrics_dict['value'] = round(data_detail.metrics.perc_lat_50,1)
          elif metric == 'p90':
            user_metrics_dict['value'] = round(data_detail.metrics.perc_lat_90,1)
          elif metric == 'p95':
            user_metrics_dict['value'] = round(data_detail.metrics.perc_lat_95,1)
          elif metric == 'p99':
            user_metrics_dict['value'] = round(data_detail.metrics.perc_lat_99,1)
          elif metric == 'p99point9':
            user_metrics_dict['value'] = round(data_detail.metrics.perc_lat_99_point_9,1)
          elif metric == 'serverSysTime':
            user_metrics_dict['value'] = round(data_detail.metrics.server_system_time,1)
          elif metric == 'serverUserTime':
            user_metrics_dict['value'] = round(data_detail.metrics.server_user_time,1)
          elif metric == 'clientSysTime':
            user_metrics_dict['value'] = round(data_detail.metrics.client_system_time,1)
          elif metric == 'clientUserTime':
            user_metrics_dict['value'] = round(data_detail.metrics.client_user_time,1)

          metricList.append(user_metrics_dict)

    return metricList
