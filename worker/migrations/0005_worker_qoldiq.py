# Generated by Django 5.2 on 2025-05-29 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worker', '0004_worker_ishlangan_worker_tolangan'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='qoldiq',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
