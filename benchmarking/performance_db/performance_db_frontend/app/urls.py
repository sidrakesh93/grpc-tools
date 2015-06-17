from django.conf.urls import patterns, url
from app import views

urlpatterns = patterns('',
  url(r'^$', views.displayLeaderboard, name='dataTable'),
  url(r'dataTable', views.displayLeaderboard, name='dataTable'),
  url(r'plotGeneral/(?P<metric>\w+)', views.plotGeneralStatistic, name='plotGeneralStatistic'),
  url(r'plotUser/(?P<clientid>\w+)', views.plotUserMetrics, name='plotUserMetrics'),
  url(r'configs', views.displayConfigs, name='configs')
)