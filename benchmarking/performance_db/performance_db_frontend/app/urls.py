from django.conf.urls import patterns, url
from app import views

urlpatterns = patterns(
    '',
    url(r'^$', views.displayPerformanceDatabase, name='data table'),
    url(r'data-table', views.displayPerformanceDatabase, name='data table'),
    url(r'plot-general/(?P<metric>\w+)', views.displayGeneralStatistic, name='plot general statistic'),
    url(r'plot-user/(?P<client_id>\w+)', views.displayUserMetrics, name='plot user metrics'),
    url(r'configs', views.displayConfigs, name='configs')
)
