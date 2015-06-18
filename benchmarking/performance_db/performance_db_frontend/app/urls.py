from django.conf.urls import patterns, url
from app import views

urlpatterns = patterns('',
  url(r'^$', views.displayPerformanceDatabase, name='dataTable'),
  url(r'dataTable', views.displayPerformanceDatabase, name='dataTable'),
  url(r'plotGeneral/(?P<metric>\w+)', views.displayGeneralStatistic, name='plotGeneralStatistic'),
  url(r'plotUser/(?P<clientid>\w+)', views.displayUserMetrics, name='plotUserMetrics'),
  url(r'configs', views.displayConfigs, name='configs')
)