from django.core.management import BaseCommand
import mesidha_backend.mesidha_executor as executor
from mesidha_backend.mailer import server_startup


class Command(BaseCommand):


    def add_arguments(self, parser):
        parser.add_argument('-i', '--init', action='store_true', help='Just init application.')

    def handle(self, *args, **kwargs):
        if kwargs['init']:
            print("Initialized!")
        server_startup()






