import json
import uuid
import os

import pandas as pd
from mesidha_backend.models import Notification

def prepare_set_file(content, file):
    with open(file, "w") as fh:
        for line in content:
            fh.write(line + "\n")

def get_uid_for_file():
    uid = uuid.uuid4()
    while os.path.exists(os.path.join("/tmp", str(uid))):
        uid = uuid.uuid4()
    return uid


def set_uid(data):
    data["uid"] = str(get_uid_for_file())
    data["out"] = os.path.join("/tmp", str(data["uid"])) + "/"
    os.mkdir(data["out"])
    prepare_mail(data)


def prepare_cluster_file(content, file):
    with open(file, "w") as fh:
        for entry in content:
            fh.write(str(entry["id"]) + "\t" + str(entry["cluster"]) + "\n")


def prepare_files(data, params):
    with open(os.path.join(data['out'], data['uid'] + "_input.json"), 'w') as fh:
        if 'network_data' in data:
            bg = data['network_data']
            del data['network_data']
            uid = data['uid']
            del data['uid']
            out = data['out']
            del data['out']
            fh.write(json.dumps(data))
            data['network_data'] = bg
            data['uid'] = uid
            data['out'] = out
        else:
            fh.write(params)
    with open(os.path.join(data['out'], data['uid'] + "_url.txt"), 'w') as fh:
        fh.write("https://masidha.zbh.uni-hamburg.de/result?id=" + data['uid'])


def toJson(data):
    dump = ""
    if 'network_data' in data:
        bg = data['network_data']
        file_name = data['network_data']['name'].rsplit('.', 1)
        suffix = ""
        if len(file_name) > 1:
            suffix = file_name[1]
        data['network_data'] = {'network_file': data['uid'] + "_network." + suffix,'prop_name':bg['prop_name'], 'id_type':bg['id_type']}

    uid = data['uid']
    del data['uid']
    out = data['out']
    del data['out']
    dump = json.dumps(data)
    data['uid'] = uid
    data['out'] = out

    if 'network_data' in data:
        data['network_data'] = bg
        data['network_data']['name'] = data['uid'] + "_network." + suffix

    return dump

def prepare_mail(data):
    if "mail" in data:
        if "sigCont" in data and data["sigCont"]:
            mail = data["mail"].strip()
            uid = data["uid"]
            n = Notification.objects.create(mail=mail, uid=uid)
            n.save()
        del data["mail"]


def prepare_set(data):
    set_uid(data)
    params = toJson(data)
    prepare_files(data, params)
    data["target"] = set(data["target"])
    return params

def prepare_subnetwork(data):
    set_uid(data)
    params = toJson(data)
    prepare_files(data, params)
    data["target"] = set(data["target"])
    return params


def prepare_subnetwork_set(data):
    set_uid(data)
    params = toJson(data)
    prepare_files(data, params)
    data["target"] = set(data["target"])
    data["reference"] = set(data["reference"])
    return params

def prepare_cluster(data):
    set_uid(data)
    params = toJson(data)
    prepare_files(data, params)
    data["target"] = pd.DataFrame.from_dict(data["target"])
    return params


def prepare_set_set(data):
    set_uid(data)
    params = toJson(data)
    prepare_files(data, params)
    data["reference"] = set(data["reference"])
    data["target"] = set(data["target"])
    return params


def prepare_id_set(data):
    set_uid(data)
    params = toJson(data)
    prepare_files(data, params)
    data["target"] = set(data["target"])
    return params
