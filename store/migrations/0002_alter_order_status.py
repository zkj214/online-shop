# Generated by Django 4.2.23 on 2025-07-21 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Open', 'Open'), ('Complete', 'Complete'), ('Shipped Out', 'Shipped Out')], default='Open', max_length=100),
        ),
    ]
