# Generated by Django 2.1 on 2019-06-28 00:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_calendarevent_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calendarevent',
            name='author',
        ),
    ]