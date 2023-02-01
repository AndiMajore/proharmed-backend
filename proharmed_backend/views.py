import base64
import mimetypes
import os
import json
import uuid
from datetime import datetime
from urllib.request import Request

import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, Http404
from rest_framework.response import Response
from django.utils.encoding import smart_str
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser

from proharmed_backend import preparation
from django.views.decorators.cache import never_cache
from database.models import Task, Attachment, Notification
from proharmed_backend.cleaner import clean_data
from proharmed_backend.task import start_task, refresh_from_redis, task_stats


@api_view(['GET'])
def clear(request) -> Response:
    uid = request.GET.get('uid')
    clean_data(uid)
    return Response({'uid': uid})


def get_delimiter(file, type):
    if type == 'tsv':
        return '\t'
    import csv
    sniffer = csv.Sniffer()
    with open(file, 'r') as fh:
        for line in fh.readlines():
            return sniffer.sniff(line).delimiter
    return ","


@api_view(['GET'])
def get_preview(request) -> Response:
    uid = request.GET.get('uid')
    name = request.GET.get('filename')
    file = os.path.join(get_wd(uid), name)
    df = pd.read_csv(file, sep=get_delimiter(file))
    return Response(df.head(5).to_json())

@api_view(['GET'])
def get_file_content(request) -> Response:
    uid = request.GET.get('uid')
    name = request.GET.get('filename')
    file = os.path.join(get_wd(uid), name)
    df = pd.read_csv(file, sep=get_delimiter(file))
    return Response(df.to_json())


@api_view(['POST'])
def get_result_column(request) -> Response:
    uid = request.data.get('uid')
    name = request.data.get('filename')
    column = request.data.get('column')
    file = os.path.join(get_wd(uid), name)
    df = pd.read_csv(file, sep=get_delimiter(file))
    return Response(list(set(df[column].fillna('').tolist())))


@never_cache
@api_view(['GET'])
def get_status(request) -> Response:
    uid = request.GET.get('task')
    task = Task.objects.get(uid=uid)
    if not task.done and not task.failed:
        refresh_from_redis(task)
        task.save()
    response = Response({
        'task': task.uid,
        'output': task.result,
        'failed': task.failed,
        'done': task.done,
        'status': task.status,
        'deleted': task.deleted,
        'stats': task_stats(task),
        'mode': task.mode,
        'progress': task.progress
    })
    return response


@never_cache
@api_view(['GET'])
def get_result_file_list(request) -> Response:
    uid = request.GET.get('task')
    files = list({'name': a.name} for a in Attachment.objects.filter(uid=uid))
    return (Response(files))


def get_result_file(request) -> Response:
    name = request.GET.get('name')
    a = Attachment.objects.get(name=name)
    type = ""
    if a.type == 'csv':
        type = 'text/csv'
    elif a.type == 'png':
        type = 'image/png'
    elif a.type == 'zip':
        type = 'application/zip'
    response = HttpResponse(base64.b64decode(a.content), content_type=type)
    response['Content-Disposition'] = f'attachment; filename="{name}"'
    return response


@api_view(['GET'])
def download_file(request) -> Response:
    attachment = Attachment.objects.filter(uid=request.GET.get('uid'), name=request.GET.get('filename')).first()
    # Open the file for reading content
    file = attachment.path

    if file is not None:
        response = StreamingHttpResponse(FileWrapper(open(file, 'rb'), 512), content_type=mimetypes.guess_type(file)[0])
        response['Content-Disposition'] = 'attachment; filename=' + smart_str(attachment.name)
        response['Content-Length'] = os.path.getsize(file)
        return response
    raise Http404


def get_uid():
    uid = str(uuid.uuid4())
    while Task.objects.filter(uid=uid).exists() or os.path.exists(get_wd(uid)):
        uid = str(uuid.uuid4())
    return uid


def get_wd(uid):
    return os.path.join("/tmp", uid) + "/"


def get_file_path(uid, name):
    return os.path.join(get_wd(uid), name)


def write_file(uid, file):
    fs = FileSystemStorage(location=get_wd(uid))
    fs.save(file.name, file)
    path = get_file_path(uid, file.name)
    return path


def save_file(uid, request: Request):
    wd = get_wd(uid)
    if not os.path.exists(wd):
        os.mkdir(get_wd(uid))
    file = request.FILES.get('file')
    path = write_file(uid, file)
    Attachment.objects.create(uid=uid, name=file.name, path=path, created=datetime.now())
    return file.name


@never_cache
@api_view(['GET'])
def init_task(req) -> Response:
    uid = get_uid()
    t = Task.objects.create(uid=uid, created_at=datetime.now(), mode=req.GET.get('mode'), directory=get_wd(uid))
    return Response({'uid': t.uid})


@api_view(['GET'])
def get_input(req) -> Response:
    uid = req.GET.get('uid')
    return Response(json.loads(Task.objects.get(uid=uid).parameters))


@api_view(['POST'])
def run(req) -> Response:
    uid = req.data.get('uid')
    if 'mail' in req.data:
        mail = req.data.get('mail')
        Notification.objects.create(uid=uid, mail=mail)
        del req.data['mail']
    task = Task.objects.get(uid=uid)
    task.parameters = json.dumps(req.data)
    start_task(task)
    task.save()
    return Response({'uid': uid})


@api_view(['POST'])
def save_network(req) -> Response:
    uid = req.data.get('uid')
    task = Task.objects.get(uid=uid)
    task.parameters = json.dumps(req.data)
    task.started_at = datetime.now()
    task.finished_at = datetime.now()
    task.done = True
    task.save()
    return Response({'uid': uid})


@api_view(['POST'])
@csrf_exempt
@parser_classes([MultiPartParser])
def upload_file(req) -> Response:
    if req.method == 'POST':
        uid = req.data.get('uid')
        name = save_file(uid, req)
        return Response({"id": uid, "filename": name})
    return Response()
