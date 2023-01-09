"""mesidha_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from mesidha_backend.views import set, set_set, subnetwork, subnetwork_set, cluster, get_files, get_status, get_result, \
    get_result_file_list, get_result_file, get_network_file, get_sc_status,get_sc_results,get_sc_top_results,run_examples, download_file, upload_file

urlpatterns = [
    path('set_set', set_set),
    path('set', set),
    path('subnetwork', subnetwork),
    path('subnetwork_set', subnetwork_set),
    path('clustering', cluster),
    path('network_file', get_network_file),
    path('files', get_files),
    path('status', get_status),
    path('result', get_result),
    path('result_file_list', get_result_file_list),
    path('result_file', get_result_file),
    path('sc_status', get_sc_status),
    path('sc_results', get_sc_results),
    path('sc_top_results', get_sc_top_results),
    path('run_examples', run_examples),
    path('download_file', download_file),
    path('upload_file', upload_file)
    # path('update',run_update),
    # path('sig_cont', run_sig_cont)
]
