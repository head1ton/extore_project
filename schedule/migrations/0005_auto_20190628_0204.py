# Generated by Django 2.1 on 2019-06-28 02:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_calendarevent_author'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='calendarevent',
            options={'ordering': ['-start'], 'verbose_name': 'Event', 'verbose_name_plural': 'Events'},
        ),
    ]
