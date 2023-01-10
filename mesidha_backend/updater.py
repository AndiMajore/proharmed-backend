# import os
# from celery import shared_task
from celery.utils.log import get_task_logger

# import mesidha_backend.mesidha_executor
# import json

logger = get_task_logger(__name__)


def read_file(file):
    data = ""
    with open(file) as fh:
        while True:
            line = fh.readline().strip()
            if line is None or line == "":
                break
            data += line
    return data


# def run_examples():
#     from mesidha_backend.views import run_set, run_cluster, run_subnetwork
#     for example in examples:
#         if example[0] == 'set':
#             run_set(example[1])
#         if example[0] == 'clustering':
#             run_cluster(example[1])
#         if example[0] == 'subnetwork':
#             run_subnetwork(example[1])
