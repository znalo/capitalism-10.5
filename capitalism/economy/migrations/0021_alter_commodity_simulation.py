# Generated by Django 3.2.9 on 2022-02-13 16:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('economy', '0020_auto_20220213_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commodity',
            name='simulation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='economy.simulation'),
        ),
    ]
