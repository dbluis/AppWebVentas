# Generated by Django 5.0.6 on 2024-08-04 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_ventas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venta',
            name='fecha',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
