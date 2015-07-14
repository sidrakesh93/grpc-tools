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
"""Fetches user data from performance database server."""

import re

from collections import defaultdict
from django import conf

import perf_db_pb2
import qpstest_pb2


class UserData(object):
  """Class to communicate with performance database server."""

  def __init__(self):
    """Initializes hostname and port of database server."""
    self.hostname = conf.settings.PERF_DB_HOSTNAME
    self.port = conf.settings.PERF_DB_PORT

  def init_single_data_dict(self, test_name, timestamp, client_config,
                            server_config, sys_info, tag):
    """Initialize a single metric record dictionary."""
    single_data_dict = {
        'test_name': test_name,
        'timestamp': timestamp,
        'client_config': self.get_client_config_dict(client_config),
        'server_config': self.get_server_config_dict(server_config),
        'sys_info': self.get_sys_info_dict(sys_info),
        'tag': tag
    }
    return single_data_dict

  def get_single_user_data(self, user_id):
    """Returns a single user's data."""

    # Create Stub to communicate with performance database server
    with perf_db_pb2.early_adopter_create_PerfDbTransfer_stub(
        self.hostname, self.port) as stub:
      single_user_retrieve_request = perf_db_pb2.SingleUserRetrieveRequest()
      single_user_retrieve_request.user_id = user_id

      timeouts_secs = 10  # Max waiting time before timeout, in seconds

      # Request data and receive data from performance database server
      user_data_future = stub.RetrieveSingleUserData.async(
          single_user_retrieve_request, timeouts_secs)
      user_data = user_data_future.result()

      # Sort the data
      sorted_user_data = sorted(user_data.single_user_data.data_details,
                                key=lambda data_detail: data_detail.timestamp)

      # Lists for various metrics
      qps_list = []
      qps_per_core_list = []
      lat_list = []
      times_list = []

      for data_detail in sorted_user_data:
        if data_detail.metrics.qps != 0.0:  # qps present
          single_data_dict = self.init_single_data_dict(
              str(data_detail.test_name), str(data_detail.timestamp),
              data_detail.client_config, data_detail.server_config,
              data_detail.sys_info, str(data_detail.tag))
          single_data_dict['qps'] = round(data_detail.metrics.qps, 1)
          qps_list.append(single_data_dict)

        if data_detail.metrics.qps_per_core != 0.0:  # qps per core present
          single_data_dict = self.init_single_data_dict(
              str(data_detail.test_name), str(data_detail.timestamp),
              data_detail.client_config, data_detail.server_config,
              data_detail.sys_info, str(data_detail.tag))
          single_data_dict['qps_per_core'] = round(
              data_detail.metrics.qps_per_core, 1)
          qps_per_core_list.append(single_data_dict)

        # percentile latenices present
        if (data_detail.metrics.perc_lat_50 != 0.0 and
            data_detail.metrics.perc_lat_90 != 0.0 and
            data_detail.metrics.perc_lat_95 != 0.0 and
            data_detail.metrics.perc_lat_99 != 0.0 and
            data_detail.metrics.perc_lat_99_point_9 != 0.0):
          single_data_dict = self.init_single_data_dict(
              str(data_detail.test_name), str(data_detail.timestamp),
              data_detail.client_config, data_detail.server_config,
              data_detail.sys_info, str(data_detail.tag))

          lat_dict = {
              'perc_lat_50': round(data_detail.metrics.perc_lat_50, 1),
              'perc_lat_90': round(data_detail.metrics.perc_lat_90, 1),
              'perc_lat_95': round(data_detail.metrics.perc_lat_95, 1),
              'perc_lat_99': round(data_detail.metrics.perc_lat_99, 1),
              'perc_lat_99_point_9': round(
                  data_detail.metrics.perc_lat_99_point_9, 1)
          }

          single_data_dict['lat'] = lat_dict
          lat_list.append(single_data_dict)

        # Server and client times present
        if (data_detail.metrics.server_system_time != 0.0 and
            data_detail.metrics.server_user_time != 0.0 and
            data_detail.metrics.client_system_time != 0.0 and
            data_detail.metrics.client_user_time != 0.0):
          single_data_dict = self.init_single_data_dict(
              str(data_detail.test_name), str(data_detail.timestamp),
              data_detail.client_config, data_detail.server_config,
              data_detail.sys_info, str(data_detail.tag))

          times_dict = {
              'server_system_time': round(
                  data_detail.metrics.server_system_time, 1),
              'server_user_time': round(data_detail.metrics.server_user_time,
                                        1),
              'client_system_time': round(
                  data_detail.metrics.client_system_time, 1),
              'client_user_time': round(data_detail.metrics.client_user_time, 1)
          }

          single_data_dict['times'] = times_dict
          times_list.append(single_data_dict)

      data_dict = defaultdict(list)
      data_dict = {
          'qpsData': qps_list,
          'qpsPerCoreData': qps_per_core_list,
          'latData': lat_list,
          'timesData': times_list
      }

      # Return user's personal details and user's data
      return [user_data.single_user_data.username, data_dict]

  def valid_value(self, val):
    """Returns non-zero value if present."""
    if val != 0.0:
      return round(val, 1)
    else:
      return '-'

  def get_server_config_dict(self, server_config):
    """Returns server configuration dictionary."""
    server_config_dict = {
        'Threads': str(server_config.threads),
        'Enable SSL': str(server_config.enable_ssl)
    }

    if server_config.server_type == qpstest_pb2.SYNCHRONOUS_SERVER:
      server_config_dict['Server Type'] = 'Synchronous'
    elif server_config.server_type == qpstest_pb2.ASYNC_SERVER:
      server_config_dict['Server Type'] = 'Asynchronous'

    return server_config_dict

  def get_client_config_dict(self, client_config):
    """Returns client configuration dictionary."""
    client_config_dict = {
        'Outstanding RPCs Per Channel': str(
            client_config.outstanding_rpcs_per_channel),
        'Client Channels': str(client_config.client_channels),
        'Payload Size': str(client_config.payload_size),
        'Enable SSL': str(client_config.enable_ssl)
    }

    if client_config.client_type == qpstest_pb2.SYNCHRONOUS_CLIENT:
      client_config_dict['Client Type'] = 'Synchronous'
    elif client_config.client_type == qpstest_pb2.ASYNC_CLIENT:
      client_config_dict['Client Type'] = 'Asynchronous'
      client_config_dict['Asynchronous Client Threads'] = str(
          client_config.async_client_threads
      )  # Set number of async client threads only in case of async

    if client_config.rpc_type == qpstest_pb2.UNARY:
      client_config_dict['RPC Type'] = 'Unary'
    elif client_config.rpc_type == qpstest_pb2.STREAMING:
      client_config_dict['RPC Type'] = 'Streaming'

    return client_config_dict

  def get_sys_info_dict(self, sys_info):
    """Returns system information dictionary."""
    sys_info_dict = {}

    sys_info = sys_info.lstrip('\'')
    sys_info = sys_info.rstrip('\\n\'')

    sys_info_list = sys_info.split('\\n\', \'')

    for sys_info_str in sys_info_list:
      sys_info_param_list = re.split(':', sys_info_str)

      sys_param_value = sys_info_param_list[1].lstrip(' ')
      sys_info_dict[str(sys_info_param_list[0])] = str(sys_param_value)

    return sys_info_dict

  def get_all_users_data(self):
    """Returns all the user's data for database table."""
    metrics_table = []

    # Create Stub to communicate with performance database server
    with perf_db_pb2.early_adopter_create_PerfDbTransfer_stub(
        self.hostname, self.port) as stub:
      all_users_retrieve_request = perf_db_pb2.AllUsersRetrieveRequest()

      timeouts_secs = 10  # Max waiting time before timeout, in seconds

      # Request data and receive data from performance database server
      # asynchronously
      all_users_data_future = stub.RetrieveAllUsersData.async(
          all_users_retrieve_request, timeouts_secs)
      all_users_data = all_users_data_future.result()

      for user_data in all_users_data.all_users_data:
        for data_detail in user_data.data_details:
          user_metrics_dict = {
              'hashed_id': str(user_data.hashed_id),
              'username': str(user_data.username),
              'timestamp': str(data_detail.timestamp),
              'test_name': str(data_detail.test_name),
              'qps': str(self.valid_value(data_detail.metrics.qps)),
              'qps_per_core': str(
                  self.valid_value(data_detail.metrics.qps_per_core)),
              'perc_lat_50': str(
                  self.valid_value(data_detail.metrics.perc_lat_50)),
              'perc_lat_90': str(
                  self.valid_value(data_detail.metrics.perc_lat_90)),
              'perc_lat_95': str(
                  self.valid_value(data_detail.metrics.perc_lat_95)),
              'perc_lat_99': str(
                  self.valid_value(data_detail.metrics.perc_lat_99)),
              'perc_lat_99_point_9': str(
                  self.valid_value(data_detail.metrics.perc_lat_99_point_9)),
              'server_system_time': str(
                  self.valid_value(data_detail.metrics.server_system_time)),
              'server_user_time': str(
                  self.valid_value(data_detail.metrics.server_user_time)),
              'client_system_time': str(
                  self.valid_value(data_detail.metrics.client_system_time)),
              'client_user_time': str(
                  self.valid_value(data_detail.metrics.client_user_time)),
              'server_config': self.get_server_config_dict(
                  data_detail.server_config),
              'client_config': self.get_client_config_dict(
                  data_detail.client_config),
              'sys_info': self.get_sys_info_dict(data_detail.sys_info),
              'tag': str(data_detail.tag)
          }
          metrics_table.append(user_metrics_dict)

    return metrics_table

  def get_all_users_single_metric_data(self, metric):
    """Returns a particular metric data for all the users."""
    metric_list = []

    # Create Stub to communicate with performance database server
    with perf_db_pb2.early_adopter_create_PerfDbTransfer_stub(
        self.hostname, self.port) as stub:
      all_users_retrieve_request = perf_db_pb2.AllUsersRetrieveRequest()

      timeouts_secs = 10  # Max waiting time before timeout, in seconds

      # Request data and receive data from performance database server
      # asynchronously
      all_users_data_future = stub.RetrieveAllUsersData.async(
          all_users_retrieve_request, timeouts_secs)
      all_users_data = all_users_data_future.result()

      for user_data in all_users_data.all_users_data:
        for data_detail in user_data.data_details:
          value = {
              'qps': round(data_detail.metrics.qps, 1),
              'qpspercore': round(data_detail.metrics.qps_per_core, 1),
              'perc50': round(data_detail.metrics.perc_lat_50, 1),
              'perc90': round(data_detail.metrics.perc_lat_90, 1),
              'perc95': round(data_detail.metrics.perc_lat_95, 1),
              'perc99': round(data_detail.metrics.perc_lat_99, 1),
              'perc99point9': round(data_detail.metrics.perc_lat_99_point_9, 1),
              'serversystime': round(data_detail.metrics.server_system_time, 1),
              'serverusertime': round(data_detail.metrics.server_user_time, 1),
              'clientsystime': round(data_detail.metrics.client_system_time, 1),
              'clientusertime': round(data_detail.metrics.client_user_time, 1)
          }[metric]

          user_metrics_dict = {
              'timestamp': str(data_detail.timestamp),
              'value': value
          }

          metric_list.append(user_metrics_dict)

    return metric_list
