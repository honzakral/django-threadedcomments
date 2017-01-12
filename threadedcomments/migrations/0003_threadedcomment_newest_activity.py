# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('threadedcomments', '0002_auto_20150521_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='threadedcomment',
            name='newest_activity',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
