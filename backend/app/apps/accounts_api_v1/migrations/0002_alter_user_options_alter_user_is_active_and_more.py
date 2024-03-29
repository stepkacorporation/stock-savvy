# Generated by Django 5.0.2 on 2024-02-29 15:04

import apps.accounts_api_v1.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts_api_v1', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('username',)},
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='is active'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='Enter a username containing 4-20 characters. It can only contain letters, hyphens, and underscores.', max_length=20, unique=True, validators=[apps.accounts_api_v1.validators.validate_username], verbose_name='username'),
        ),
    ]
