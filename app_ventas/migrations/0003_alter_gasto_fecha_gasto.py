# Generated by Django 5.0.6 on 2024-08-04 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_ventas', '0002_alter_venta_fecha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gasto',
            name='fecha_gasto',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
