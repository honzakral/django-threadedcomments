# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('threadedcomments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='threadedcomment',
            name='tree_path',
            field=models.CharField(verbose_name='Tree path', max_length=500, editable=False, db_index=False),
            preserve_default=True,
        ),
    ]
