# Generated by Django 5.0.4 on 2024-04-28 12:03

import user_auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='customuser',
            managers=[
                ('objects', user_auth.models.CustomUserManager()),
            ],
        ),
    ]
