import datetime

from django.db import models


class Task(models.Model):
    uid = models.CharField(max_length=36, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    directory = models.CharField(max_length=256)

    mode = models.CharField(max_length=32, choices=[('filter', 'filter'), ('remap', 'remap'), ('reduce', 'reduce'),
                                                    ('ortho', 'ortho')])
    parameters = models.TextField(null=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    worker_id = models.CharField(max_length=128, null=True)
    job_id = models.CharField(max_length=128, null=True)
    done = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    started = models.BooleanField(default=False)
    status = models.CharField(max_length=255, null=True)
    progress = models.FloatField(default=0.0)


class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.CharField(max_length=36, null=False)
    mail = models.CharField(max_length=128, null=False)


class Attachment(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(null=True, default=datetime.datetime.now())
    uid = models.CharField(max_length=36)
    remove = models.BooleanField(default=True)
    name = models.CharField(max_length=128)
    path = models.CharField(max_length=256)
