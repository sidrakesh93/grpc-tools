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

import user_data_pb2
import qpstest_pb2
import re
from collections import defaultdict
from django.conf import settings

# Class to communicate with performance database server
class UserData(object):

  def __init__(self, database):
    # Set hostname and port
    self.hostname = settings.PERF_DB_HOSTNAME
    self.port = settings.PERF_DB_PORT

  # Returns a dictionary of parsed time
  def parseTimeString(self, timeString):
    parsedTimeList = re.split('\W+', timeString)
    parsed = {}
    parsed['month'] = parsedTimeList[0]
    parsed['day'] = parsedTimeList[1]
    parsed['year'] = parsedTimeList[2]
    parsed['hour'] = parsedTimeList[3]
    parsed['min'] = parsedTimeList[4]
    parsed['sec'] = parsedTimeList[5]
    return parsed

  # Initialize a single metric record dictionary
  def initSingleDataDict(self, testName, timestamp, clientConfig, serverConfig, sysInfo):
    singleDataDict = {}
    singleDataDict['test_name'] = testName;
    singleDataDict['timestamp'] = self.parseTimeString(timestamp)
    singleDataDict['client_config'] = self.getClientConfigDict(clientConfig)
    singleDataDict['server_config'] = self.getServerConfigDict(serverConfig)
    singleDataDict['sys_info'] = self.getSysInfoDict(sysInfo)

    return singleDataDict

  # Returns a single user's data
  def getSingleUserData(self, userId):
    # Create Stub to communicate with performance database server
    with user_data_pb2.early_adopter_create_UserDataTransfer_stub(self.hostname, self.port) as stub:
      singleUserRetrieveRequest = user_data_pb2.SingleUserRetrieveRequest()
      singleUserRetrieveRequest.user_id = userId
      
      _TIMEOUT_SECONDS = 10 # Max waiting time before timeout, in seconds

      # Request data and receive data from performance database server asynchronously
      userData_future = stub.RetrieveSingleUserData.async(singleUserRetrieveRequest, _TIMEOUT_SECONDS)
      userData = userData_future.result()

      # Sort the data
      sortedClientData = sorted(userData.details.data_details, key=lambda dataDetail: dataDetail.timestamp)

      # Lists for various metrics
      qpsList = []
      qpsPerCoreList = []
      latList = []
      timesList = []

      for dataDetail in sortedClientData:
        if dataDetail.metrics.qps != 0.0: # qps present
          singleDataDict = self.initSingleDataDict(dataDetail.test_name, dataDetail.timestamp, dataDetail.client_config, dataDetail.server_config, dataDetail.sys_info)
          singleDataDict['qps'] = round(dataDetail.metrics.qps,1)
          qpsList.append(singleDataDict)

        if dataDetail.metrics.qps_per_core != 0.0: # qps per core present
          singleDataDict = self.initSingleDataDict(dataDetail.test_name, dataDetail.timestamp, dataDetail.client_config, dataDetail.server_config, dataDetail.sys_info)
          singleDataDict['qps_per_core'] = round(dataDetail.metrics.qps_per_core,1)
          qpsPerCoreList.append(singleDataDict)
        
        if dataDetail.metrics.perc_lat_50 != 0.0 and dataDetail.metrics.perc_lat_90 != 0.0 and dataDetail.metrics.perc_lat_95 != 0.0 and dataDetail.metrics.perc_lat_99 != 0.0 and dataDetail.metrics.perc_lat_99_point_9 != 0.0: # percentile latenices present
          singleDataDict = self.initSingleDataDict(dataDetail.test_name, dataDetail.timestamp, dataDetail.client_config, dataDetail.server_config, dataDetail.sys_info)
          
          latDict = {}
          latDict['perc_lat_50'] = round(dataDetail.metrics.perc_lat_50,1)
          latDict['perc_lat_90'] = round(dataDetail.metrics.perc_lat_90,1)
          latDict['perc_lat_95'] = round(dataDetail.metrics.perc_lat_95,1)
          latDict['perc_lat_99'] = round(dataDetail.metrics.perc_lat_99,1)
          latDict['perc_lat_99_point_9'] = round(dataDetail.metrics.perc_lat_99_point_9,1)

          singleDataDict['lat'] = latDict
          latList.append(singleDataDict)
        
        if dataDetail.metrics.server_system_time != 0.0 and dataDetail.metrics.server_user_time != 0.0 and dataDetail.metrics.client_system_time != 0.0 and dataDetail.metrics.client_user_time != 0.0: # Server and client times present
          singleDataDict = self.initSingleDataDict(dataDetail.test_name, dataDetail.timestamp, dataDetail.client_config, dataDetail.server_config, dataDetail.sys_info)

          timesDict = {}
          timesDict['server_system_time'] = round(dataDetail.metrics.server_system_time,1)
          timesDict['server_user_time'] = round(dataDetail.metrics.server_user_time,1)
          timesDict['client_system_time'] = round(dataDetail.metrics.client_system_time,1)
          timesDict['client_user_time'] = round(dataDetail.metrics.client_user_time,1)
          
          singleDataDict['times'] = timesDict
          timesList.append(singleDataDict)

      dataDict = defaultdict(list)
      dataDict['qpsData'] = qpsList
      dataDict['qpsPerCoreData'] = qpsPerCoreList
      dataDict['latData'] = latList
      dataDict['timesData'] = timesList

      # Return user's personal details and user's data
      return [userData.details.user_details, dataDict]

  # If non-zero value present, returns it
  def validValue(self, val):
    if val != 0.0:
      return round(val,1)
    else:
      return '-'

  # Returns server configuration dictionary
  def getServerConfigDict(self, serverConfig):
    serverConfigDict = {}

    if serverConfig.server_type == qpstest_pb2.SYNCHRONOUS_SERVER:
      serverConfigDict['Server Type'] = 'Synchronous'
    elif serverConfig.server_type == qpstest_pb2.ASYNC_SERVER:
      serverConfigDict['Server Type'] = 'Asynchronous'

    serverConfigDict['Threads'] = str(serverConfig.threads)
    serverConfigDict['Enable SSL'] = str(serverConfig.enable_ssl)
    # serverConfigDict['Host'] = str(serverConfig.host)

    return serverConfigDict

  # Returns client configuration dictionary
  def getClientConfigDict(self, clientConfig):
    clientConfigDict = {}

    # serverTargets = []
    # for serverTarget in clientConfig.server_targets:
    #   serverTargets.append(str(serverTarget))
    # serverTargetsStr = ', '.join(serverTargets)
    # clientConfigDict['Server Targets'] = serverTargetsStr

    if clientConfig.client_type == qpstest_pb2.SYNCHRONOUS_CLIENT:
      clientConfigDict['Client Type'] = 'Synchronous'
    elif clientConfig.client_type == qpstest_pb2.ASYNC_CLIENT:
      clientConfigDict['Client Type'] = 'Asynchronous'
      clientConfigDict['Asynchronous Client Threads'] = str(clientConfig.async_client_threads)

    clientConfigDict['Outstanding RPCs Per Channel'] = str(clientConfig.outstanding_rpcs_per_channel)
    clientConfigDict['Client Channels'] = str(clientConfig.client_channels)
    clientConfigDict['Payload Size'] = str(clientConfig.payload_size)
    
    if clientConfig.rpc_type == qpstest_pb2.UNARY:
      clientConfigDict['RPC Type'] = 'Unary'
    elif clientConfig.rpc_type == qpstest_pb2.STREAMING:
      clientConfigDict['RPC Type'] = 'Streaming'

    clientConfigDict['Enable SSL'] = str(clientConfig.enable_ssl)
    # clientConfigDict['Host'] = str(clientConfig.host)

    return clientConfigDict

  # Returns system information dictionary
  def getSysInfoDict(self, sysInfo):
    sysInfoDict = {}

    sysInfo = sysInfo.lstrip('\'')
    sysInfo = sysInfo.rstrip('\\n\'')

    sysInfoList = sysInfo.split('\\n\', \'')

    for sysInfoStr in sysInfoList:
      sysInfoParamList = re.split(':', sysInfoStr)

      sysParamValue = sysInfoParamList[1].lstrip(' ')
      sysInfoDict[str(sysInfoParamList[0])] = str(sysParamValue)

    return sysInfoDict

  # Returs all the user's data for database table
  def getAllUsersData(self):
    metricsTable = []

    # Create Stub to communicate with performance database server
    with user_data_pb2.early_adopter_create_UserDataTransfer_stub(self.hostname, self.port) as stub:
      allUsersRetrieveRequest = user_data_pb2.AllUsersRetrieveRequest()

      _TIMEOUT_SECONDS = 10 # Max waiting time before timeout, in seconds

      # Request data and receive data from performance database server asynchronously
      allUsersData_future = stub.RetrieveAllUsersData.async(allUsersRetrieveRequest, _TIMEOUT_SECONDS)
      allUsersData = allUsersData_future.result()

      for userData in allUsersData.user_data:
        for dataDetail in userData.data_details:
          userMetricsDict = {}
          userMetricsDict['id'] = str(userData.user_details.id)
          userMetricsDict['name'] = str(userData.user_details.name)
          userMetricsDict['timestamp'] = self.parseTimeString(dataDetail.timestamp)
          userMetricsDict['test_name'] = str(dataDetail.test_name)
          userMetricsDict['qps'] = str(self.validValue(dataDetail.metrics.qps))
          userMetricsDict['qps_per_core'] = str(self.validValue(dataDetail.metrics.qps_per_core))
          userMetricsDict['perc_lat_50'] = str(self.validValue(dataDetail.metrics.perc_lat_50))
          userMetricsDict['perc_lat_90'] = str(self.validValue(dataDetail.metrics.perc_lat_90))
          userMetricsDict['perc_lat_95'] = str(self.validValue(dataDetail.metrics.perc_lat_95))
          userMetricsDict['perc_lat_99'] = str(self.validValue(dataDetail.metrics.perc_lat_99))
          userMetricsDict['perc_lat_99_point_9'] = str(self.validValue(dataDetail.metrics.perc_lat_99_point_9))
          userMetricsDict['server_system_time'] = str(self.validValue(dataDetail.metrics.server_system_time))
          userMetricsDict['server_user_time'] = str(self.validValue(dataDetail.metrics.server_user_time))
          userMetricsDict['client_system_time'] = str(self.validValue(dataDetail.metrics.client_system_time))
          userMetricsDict['client_user_time'] = str(self.validValue(dataDetail.metrics.client_user_time))
          userMetricsDict['server_config'] = self.getServerConfigDict(dataDetail.server_config)
          userMetricsDict['client_config'] = self.getClientConfigDict(dataDetail.client_config)
          userMetricsDict['sys_info'] = self.getSysInfoDict(dataDetail.sys_info)

          metricsTable.append(userMetricsDict)

    return metricsTable

  # Returns a particular metric data for all the users
  def getAllUsersSingleMetricData(self, metric):
    metricList = []

    # Create Stub to communicate with performance database server
    with user_data_pb2.early_adopter_create_UserDataTransfer_stub(self.hostname, self.port) as stub:
      allUsersRetrieveRequest = user_data_pb2.AllUsersRetrieveRequest()

      _TIMEOUT_SECONDS = 10 # Max waiting time before timeout, in seconds

      # Request data and receive data from performance database server asynchronously
      allUsersData_future = stub.RetrieveAllUsersData.async(allUsersRetrieveRequest, _TIMEOUT_SECONDS)
      allUsersData = allUsersData_future.result()

      for userData in allUsersData.user_data:
        for dataDetail in userData.data_details:
          userMetricsDict = self.parseTimeString(dataDetail.timestamp)

          if metric == 'QPS':
            userMetricsDict['value'] = round(dataDetail.metrics.qps,1)
          elif metric == 'qpsPerCore':
            userMetricsDict['value'] = round(dataDetail.metrics.qps_per_core,1)
          elif metric == 'p50':
            userMetricsDict['value'] = round(dataDetail.metrics.perc_lat_50,1)
          elif metric == 'p90':
            userMetricsDict['value'] = round(dataDetail.metrics.perc_lat_90,1)
          elif metric == 'p95':
            userMetricsDict['value'] = round(dataDetail.metrics.perc_lat_95,1)
          elif metric == 'p99':
            userMetricsDict['value'] = round(dataDetail.metrics.perc_lat_99,1)
          elif metric == 'p99point9':
            userMetricsDict['value'] = round(dataDetail.metrics.perc_lat_99_point_9,1)
          elif metric == 'serverSysTime':
            userMetricsDict['value'] = round(dataDetail.metrics.server_system_time,1)
          elif metric == 'serverUserTime':
            userMetricsDict['value'] = round(dataDetail.metrics.server_user_time,1)
          elif metric == 'clientSysTime':
            userMetricsDict['value'] = round(dataDetail.metrics.client_system_time,1)
          elif metric == 'clientUserTime':
            userMetricsDict['value'] = round(dataDetail.metrics.client_user_time,1)

          metricList.append(userMetricsDict)

    return metricList


