import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """django command to pause execution until db is available"""

    def handle(self, *args, **kwargs):
        """handle the command"""
        self.stdout.write('waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('database unavailable, waiting one second')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('database available!'))
