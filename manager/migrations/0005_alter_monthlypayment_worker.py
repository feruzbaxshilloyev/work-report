# Generated by Django 5.2 on 2025-05-29 12:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0004_monthlypayment'),
        ('worker', '0005_worker_qoldiq'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monthlypayment',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='worker.worker'),
        ),
    ]
