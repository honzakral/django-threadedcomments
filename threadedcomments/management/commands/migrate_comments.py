from django.core.management.base import NoArgsCommand
from django.contrib import comments
from django.db import transaction, connection
from django.conf import settings

PATH_SEPARATOR = getattr(settings, 'COMMENT_PATH_SEPARATOR', '/')
PATH_DIGITS = getattr(settings, 'COMMENT_PATH_DIGITS', 10)

SQL = """
INSERT INTO threadedcomments_comment(comment_ptr_id, tree_path) VALUES(%s, %s)
"""

class Command(NoArgsCommand):
    help = "Migrates from django.contrib.comments to django-threadedcomments"
        
    def handle(self, *args, **options):
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)
        
        cursor = connection.cursor()
        
        for comment in comments.models.Comment.objects.all():
            cursor.execute(SQL, [comment.id, ''])
        
        transaction.commit()
        transaction.leave_transaction_management()