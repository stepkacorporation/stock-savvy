# Generated by Django 5.0.2 on 2024-02-27 12:48

import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(help_text='Enter a username containing 4-20 characters. It can only contain letters, hyphens, and underscores.', max_length=20, unique=True, verbose_name='username')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('is_staff', models.BooleanField(default=False, verbose_name='is staff')),
                ('is_admin', models.BooleanField(default=False, verbose_name='is admin')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
