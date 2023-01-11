from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail

logger = get_task_logger(__name__)


@shared_task
def check_mails():
    from database.models import Notification, Task
    uids = set()
    for n in Notification.objects.all():
        if n.uid not in uids:
            uids.add(n.uid)
    for uid in uids:
        t = Task.objects.get(uid=uid)
        if t.done:
            logger.info(f"Sending mails for task {uid}")
            send_notification(uid)


def get_notification_mails(id):
    try:
        from database.models import Notification, Task
        mails = []
        for n in Notification.objects.filter(uid=id):
            mails.append(n.mail)
        return mails
    except Exception:
        print("No mailing entries fround for ID=" + id)
        return None


def send_notification(id):
    mails = get_notification_mails(id)
    if mails is not None:
        link = "https://mesidha.zbh.uni-hamburg.de/result?id=" + id
        send_mail('Your MeSIdHa job has finished',
                  f'The harmonization of your data was finished.\nCheck them out here: {link}\n\nResult and input data will be automatically removed within 24h or by earlier on the result page!',
                  'tools-cosybio.zbh@uni-hamburg.de', mails, fail_silently=True)
        remove_notification(id)


def remove_notification(id):
    from database.models import Notification, Task
    for n in Notification.objects.filter(uid=id):
        n.delete()


def error_notification(message):
    send_mail('Error in mesidha-execution', f'Message: {message}', 'tools-cosybio.zbh@uni-hamburg.de',
              ['status@andimajore.de'], True)


def server_startup():
    send_mail('MeSIdHa system startup', f'The MeSIdHa-validation backend is now ready!',
              'tools-cosybio.zbh@uni-hamburg.de', ['status@andimajore.de'], fail_silently=False)
