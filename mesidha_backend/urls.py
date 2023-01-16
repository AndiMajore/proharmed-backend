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

from mesidha_backend.views import *

urlpatterns = [
    path('result_file', get_result_file),
    path('result_file_list', get_result_file_list),

    # path('result', get_result),
    path('get_preview', get_preview),
    path('status', get_status),
    path('download_file', download_file),
    path('upload_file', upload_file),
    path('init_task', init_task),
    path('get_input', get_input),
    path('run_filter', run),
    path('run_remap', run),
    path('run_reduce', run),
    path('run_ortho', run),
    path('clear', clear),
    path('get_result_column', get_result_column)
    # path('update',run_update),
    # path('sig_cont', run_sig_cont)
]
