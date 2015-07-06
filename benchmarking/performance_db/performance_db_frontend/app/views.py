from django.shortcuts import render
from user_data import UserData

user_data = UserData()

# View for performance database table page
def displayPerformanceDatabase(request):
  all_users_data = allUsersData()
  return render(request, 'data_table.html', {'all_users_data': all_users_data})

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
  complete_data = singleUserData(clientid)
  return render(request, 'user_plots.html', {'username': complete_data[0], 'userdata': complete_data[1]})

# Returns full metric name
def getMetricFullDesc(metric):
  if metric == 'QPS':
    metric_name = 'Queries Per Second'
  elif metric == 'qpsPerCore':
    metric_name = 'QPS Per Core'
  elif metric == 'p50':
    metric_name = '50th Percentile Latency'
  elif metric == 'p90':
    metric_name = '90th Percentile Latency'
  elif metric == 'p95':
    metric_name = '95th Percentile Latency'
  elif metric == 'p99':
    metric_name = '99th Percentile Latency'
  elif metric == 'p99point9':
    metric_name = '99.9th Percentile Latency'
  elif metric == 'serverSysTime':
    metric_name = 'Server System Time'
  elif metric == 'serverUserTime':
    metric_name = 'Server User Time'
  elif metric == 'clientSysTime':
    metric_name = 'Client System Time'
  elif metric == 'clientUserTime':
    metric_name = 'Client User Time'

  return metric_name

# Returns single user data
def singleUserData(client_id):
  return user_data.getSingleUserData(client_id)

# Returns all users' data
def allUsersData():
  return user_data.getAllUsersData()

# Return all users' single metric data
def allUsersSingleMetricData(metric):
  return user_data.getAllUsersSingleMetricData(metric)
