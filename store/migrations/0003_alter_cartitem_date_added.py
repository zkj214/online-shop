# Generated by Django 4.2.23 on 2025-07-21 12:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='date_added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
