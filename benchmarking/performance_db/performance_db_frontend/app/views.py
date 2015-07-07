from django.shortcuts import render
from user_data import UserData

user_data = UserData()

def displayPerformanceDatabase(request):
  """View for performance database table page"""
  all_users_data = allUsersData()
  return render(request, 'data_table.html', {'all_users_data': all_users_data})

def displayConfigs(request):
  """View for config page"""
  return render(request, 'configs.html', {})

def displayGeneralStatistic(request, metric):
  """View for general statistic page"""
  return generalStatisticRenderer(request, metric)

def generalStatisticRenderer(request, metric):
  """General statistic page renderer"""
  data = allUsersSingleMetricData(metric)
  return render(request, 'general_plots.html', {'metric': getMetricFullDesc(metric), 'data': data})

def displayUserMetrics(request, client_id):
  """View for user metrics page"""
  complete_data = singleUserData(client_id)
  return render(request, 'user_plots.html', {'username': complete_data[0], 'userdata': complete_data[1]})

def getMetricFullDesc(metric):
  """Returns full metric name"""

  metric_name = {
      'qps': 'Queries Per Second',
      'qpspercore': 'QPS Per Core',
      'perc50': '50th Percentile Latency',
      'perc90': '90th Percentile Latency',
      'perc95': '95th Percentile Latency',
      'perc99': '99th Percentile Latency',
      'perc99point9': '99.9th Percentile Latency',
      'serversystime': 'Server System Time',
      'serverusertime': 'Server User Time',
      'clientsystime': 'Client System Time',
      'clientusertime': 'Client User Time'
  }.get(metric, 'error')

  if metric_name == 'error':
    raise Exception

  return metric_name

def singleUserData(client_id):
  """Returns single user data"""
  return user_data.getSingleUserData(client_id)

def allUsersData():
  """Returns all users' data"""
  return user_data.getAllUsersData()

def allUsersSingleMetricData(metric):
  """Return all users' single metric data"""
  return user_data.getAllUsersSingleMetricData(metric)
