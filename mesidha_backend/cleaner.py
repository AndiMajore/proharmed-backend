import datetime
import os

from celery import shared_task
from celery.utils.log import get_task_logger

from database.models import Attachment, Task, Notification

logger = get_task_logger(__name__)


def check_notification(uid):
    ns = Notification.objects.filter(uid=uid)
    if len(ns) > 0:
        ns.delete()


def clean_data(uid):
    wd = get_wd(uid)
    if os.path.exists(wd):
        os.system(f"rm -rf {get_wd(uid)}")
    Attachment.objects.filter(uid=uid).delete()
    check_notification(uid)
    print(f"Removed job {uid}")
    t = Task.objects.get(uid=uid)
    t.deleted = True
    t.save()


def get_wd(uid):
    return os.path.join("/tmp", uid) + "/"


@shared_task()
def check_cleaning():
    for t in Task.objects.all():
        now = datetime.datetime.now(datetime.timezone.utc)
        if t.finished_at is None:
            if t.started_at is not None:
                diff = now - t.started_at
                hrs = diff.total_seconds() / 60 / 60
                if hrs < 1:
                    continue
            clean_data(t.uid)
            print(f"Removed unfinished task {t.uid}")
            t.delete()
            continue
        diff = now - t.finished_at
        hrs = diff.total_seconds() / 60 / 60
        if hrs > 24:
            clean_data(t.uid)
