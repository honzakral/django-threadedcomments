# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, connection
import django.db.models.deletion

is_index = connection.vendor != 'mysql'


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThreadedComment',
            fields=[
                ('comment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='django_comments.Comment')),
                ('title', models.TextField(verbose_name='Title', blank=True)),
                ('tree_path', models.CharField(verbose_name='Tree path', max_length=500, editable=False, db_index=is_index)),
                ('last_child', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Last child', blank=True, to='threadedcomments.ThreadedComment', null=True)),
                ('parent', models.ForeignKey(related_name='children', default=None, blank=True, to='threadedcomments.ThreadedComment', null=True, verbose_name='Parent')),
            ],
            options={
                'ordering': ('tree_path',),
                'db_table': 'threadedcomments_comment',
                'verbose_name': 'Threaded comment',
                'verbose_name_plural': 'Threaded comments',
            },
            bases=('django_comments.comment',),
        )
    ]
