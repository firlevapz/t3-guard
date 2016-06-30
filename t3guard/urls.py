"""t3guard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^temperature_details/$', views.temperature_details, name='temperature-details'),
    url(r'^motion_details/$', views.motion_details, name='motion-details'),
    url(r'^motion_details/(?P<days>[0-9]*)/$', views.motion_details, name='motion-details-days'),
    url(r'^toggle_config/(?P<config_type>[A-Za-z0-9]+)/(?P<name>[A-Za-z0-9]+)(?:/(?P<value>[0-9]+))?/$', views.toggle_config, name='toggle-config'),
    url(r'^set_config_value/(?P<config_type>[A-Za-z0-9]+)/(?P<name>[A-Za-z0-9]+)(?:/(?P<value>[0-9]+))?/$', views.set_config_value, name='set-config-value'),
    url(r'^csv_temp/(?P<sensor_id>[a-z0-9]+)/$', views.csv_temperatures, name='csv-temperatures'),
]
