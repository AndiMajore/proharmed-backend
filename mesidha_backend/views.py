import base64
import mimetypes
import os
import json
import uuid
from datetime import datetime
from urllib.request import Request

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.encoding import smart_str
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser

from mesidha_backend import preparation
from django.views.decorators.cache import never_cache
from mesidha_backend.models import Task, Attachment, Notification
from mesidha_backend.task import start_task, refresh_from_redis, task_stats
from mesidha_backend.versions import get_version


def run(mode, data, params) -> Response:
    version = get_version()
    id = checkExistence(params, version, mode)
    if id is not None:
        try:
            n = Notification.objects.filter(uid=data["uid"]).first()
            n.uid = id
            n.save()
        except Exception:
            pass
        return Response({'task': id})
    sc = False
    if 'sigCont' in data and data["sigCont"]:
        sc = True
    if sc and len(data["target"]) > 100 and ('sigContTarget' not in data or len(data["sigContTarget"]) > 100):
        return Response({"task": None, "error": True, "reason": "Significance contribution calculation can only be "
                                                                "carried out for maximum 100 entries."})
    task = Task.objects.create(uid=data["uid"], mode=mode, parameters=data, request=params, version=version, sc=sc)
    start_task(task)
    task.save()
    return Response({'task': data["uid"]})


@api_view(['GET'])
def run_examples(request) -> Response:
    return Response()


def checkExistence(params, version, mode):
    try:
        entry = Task.objects.filter(request=params, mode=mode, failed=False, version=version).last()
        return entry.uid
    except:
        return None


@never_cache
@api_view(['GET'])
def get_sc_status(request) -> Response:
    uid = request.GET.get('task')
    task = Task.objects.get(uid=uid)
    status = json.loads(task.sc_status)
    response = Response({"task": uid, "done": task.sc_done, "status": status})
    return response


@api_view(['GET'])
def get_sc_top_results(request) -> Response:
    uid = request.GET.get('task')
    results = json.loads(Task.objects.get(uid=uid).sc_top_results)
    return Response(results)


@api_view(['GET'])
def get_sc_results(request) -> Response:
    uid = request.GET.get('task')
    task = Task.objects.get(uid=uid)
    response = Response(json.loads(task.sc_result))
    return response


@api_view(['POST'])
def set(request) -> Response:
    data = request.data
    params = preparation.prepare_set(data)
    return run("set", data, params)


def run_set(data):
    params = preparation.prepare_set(data)
    return run("set", data, params)


@api_view(['POST'])
def subnetwork(request) -> Response:
    data = request.data
    params = preparation.prepare_subnetwork(data)
    return run("subnetwork", data, params)


def run_subnetwork(data):
    params = preparation.prepare_subnetwork(data)
    return run("subnetwork", data, params)


@api_view(['POST'])
def subnetwork_set(request) -> Response:
    data = request.data
    params = preparation.prepare_subnetwork_set(data)
    return run("subnetwork", data, params)


def run_subnetwork_set(data):
    params = preparation.prepare_subnetwork_set(data)
    return run("subnetwork", data, params)


@api_view(['POST'])
def cluster(request) -> Response:
    data = request.data
    params = preparation.prepare_cluster(data)
    return run("cluster", data, params)


def run_cluster(data):
    params = preparation.prepare_cluster(data)
    return run("cluster", data, params)


@api_view(['POST'])
def set_set(request) -> Response:
    data = request.data
    params = preparation.prepare_set_set(data)
    return run("set-set", data, params)


def run_set_set(data):
    params = preparation.prepare_set_set(data)
    return run("set-set", data, params)


@api_view(['POST'])
def id_set(request) -> Response:
    data = request.data
    params = preparation.prepare_id_set(data)
    return run("id-set", data, params)


def run_id_set(data):
    params = preparation.prepare_id_set(data)
    return run("id-set", data, params)


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
        'failed': task.failed,
        'done': task.done,
        'status': task.status,
        'stats': task_stats(task),
        'mode': task.mode,
        'type': json.loads(task.request)["type"],
        'input': json.loads(task.request),
        'progress': task.progress
    })
    return response


@never_cache
@api_view(['GET'])
def get_result_file_list(request) -> Response:
    uid = request.GET.get('task')
    files = list({'name': a.name, 'type': a.type} for a in Attachment.objects.filter(uid=uid))
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
def get_result(request) -> Response:
    uid = request.GET.get('task')
    task = Task.objects.get(uid=uid)
    if not task.done and not task.failed:
        refresh_from_redis(task)
        task.save()
    return Response({'task': task.uid, 'result': json.loads(task.result), 'parameters': json.loads(task.request)})


@api_view(['GET'])
def get_network_file(request) -> Response:
    file = "/usr/src/mesidha/example_files/gene_network.graphml"
    if file is not None:
        response = StreamingHttpResponse(FileWrapper(open(file, 'rb'), 512), content_type=mimetypes.guess_type(file)[0])
        response['Content-Disposition'] = 'attachment; filename=' + smart_str("gene_network.graphml")
        response['Content-Length'] = os.path.getsize(file)
        return response
    raise Http404


@api_view(['GET'])
def download_file(request) -> Response:
    # Define text file name
    # TODO get file by requested name and uid
    Attachment.get_latest_by()
    # Define the full file path
    # filepath = os.path.join('data', filename)
    # # Open the file for reading content
    # path = open(filepath, 'r')
    # # Set the mime type
    # mime_type, _ = mimetypes.guess_type(filepath)
    # # Set the return value of the HttpResponse
    # response = HttpResponse(path, content_type=mime_type)
    # # Set the HTTP header for sending to browser
    # response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value
    # return response
    return Response()


def get_uid():
    uid = str(uuid.uuid4())
    while Task.objects.filter(uid=uid).exists():
        uid = str(uuid.uuid4())
    return uid


def get_wd(uid):
    return os.path.join("/tmp", uid) + "/"


def get_file_path(uid, name):
    return os.path.join(get_wd(uid), uid, name)


def write_file(uid, file):
    fs = FileSystemStorage(location=get_wd(uid))
    filename = fs.save(uid, file)
    path = get_file_path(uid, file.name)
    os.system("mv " + os.path.join(get_wd(uid), filename) + " " + path)
    return path


def save_file(uid, request: Request):
    os.mkdir(get_wd(uid))
    file = request.FILES.get('file')
    path = write_file(uid, file)
    print(path)
    # Attachment.objects.create(uid=uid, input=False, filename=file.name, path=path, created=datetime.now())


@api_view(['POST'])
@csrf_exempt
@parser_classes([MultiPartParser])
def upload_file(req) -> Response:
    if req.method == 'POST':
        # uid = get_uid()
        uid = req.FILES.get('uid').name
        save_file(uid, req)
        return Response({"id": uid})
    return Response()


@api_view(['GET'])
def get_files(request) -> Response:
    file_name = request.GET.get('name')
    measure = request.GET.get('measure')
    file = file_name
    if not file_name.endswith(".csv") and measure is not None:
        file = os.path.join(measure, file_name)
    # file = digest_files.getFile(file)
    if file is not None:
        response = StreamingHttpResponse(FileWrapper(open(file, 'rb'), 512), content_type=mimetypes.guess_type(file)[0])
        response['Content-Disposition'] = 'attachment; filename=' + smart_str(file_name)
        response['Content-Length'] = os.path.getsize(file)
        return response
    raise Http404
