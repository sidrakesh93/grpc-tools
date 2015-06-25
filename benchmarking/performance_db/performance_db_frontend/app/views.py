from django.shortcuts import render
from user_data import UserData

# View for performance database table page
def displayPerformanceDatabase(request):
  metricstable = allUsersData()
  return render(request, 'data_table.html', {'metricstable': metricstable})

# View for config page
def displayConfigs(request):
  return render(request, 'configs.html', {})

# View for general statistic page
def displayGeneralStatistic(request, metric):
  return generalStatisticRenderer(request, metric)

# General statistic page renderer
def generalStatisticRenderer(request, metric):
  data = allUsersSingleMetricData(metric)
  return render(request, 'general_plots.html', {'metric': getMetricFullDesc(metric), 'data': data})

# View for user metrics page
def displayUserMetrics(request, clientid):
  completeData = singleUserData(clientid)
  return render(request, 'user_plots.html', {'user_info': completeData[0], 'userdata': completeData[1]})

# Returns full metric name
def getMetricFullDesc(metric):
  if metric == 'QPS':
    metricName = 'Queries Per Second'
  elif metric == 'qpsPerCore':
    metricName = 'QPS Per Core'
  elif metric == 'p50':
    metricName = '50th Percentile Latency'
  elif metric == 'p90':
    metricName = '90th Percentile Latency'
  elif metric == 'p95':
    metricName = '95th Percentile Latency'
  elif metric == 'p99':
    metricName = '99th Percentile Latency'
  elif metric == 'p99point9':
    metricName = '99.9th Percentile Latency'
  elif metric == 'serverSysTime':
    metricName = 'Server System Time'
  elif metric == 'serverUserTime':
    metricName = 'Server User Time'
  elif metric == 'clientSysTime':
    metricName = 'Client System Time'
  elif metric == 'clientUserTime':
    metricName = 'Client User Time'

  return metricName

# Returns single user data
def singleUserData(clientId):
  userData = UserData('/tmp/clientmetricsdb')
  return userData.getSingleUserData(clientId)

# Returns all users' data
def allUsersData():
  userData = UserData('/tmp/clientmetricsdb')
  return userData.getAllUsersData()

# Return all users' single metric data
def allUsersSingleMetricData(metric):
  userData = UserData('/tmp/clientmetricsdb')
  return userData.getAllUsersSingleMetricData(metric)
