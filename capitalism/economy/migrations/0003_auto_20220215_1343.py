# Generated by Django 3.2.9 on 2022-02-15 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('economy', '0002_remove_stock_stock_owner_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timestamp',
            options={},
        ),
        migrations.RemoveField(
            model_name='timestamp',
            name='time_stamp',
        ),
    ]
