from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.db import connection, transaction

PATH_DIGITS = getattr(settings, 'COMMENT_PATH_DIGITS', 10)

SQL = """
INSERT INTO threadedcomments_comment (
    comment_ptr_id, 
    parent_id, 
    last_child_id, 
    tree_path,
    title
) 
SELECT id as comment_ptr_id, 
       null as parent_id, 
       null as last_child_id, 
       (SELECT TO_CHAR(id, '%s')) AS tree_path,
       ''
FROM django_comments;
""" % ''.zfill(PATH_DIGITS)


class Command(BaseCommand):
    help = "Migrates from django.contrib.comments to django-threadedcomments"

    def handle(self, *args, **options):
        if args:
            raise CommandError("Command doesn't accept any arguments")

        with transaction.atomic():
            cursor = connection.cursor()
            cursor.execute(SQL)
