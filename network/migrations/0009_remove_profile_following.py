# Generated by Django 3.2.6 on 2022-07-27 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_alter_user_first_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='following',
        ),
    ]
