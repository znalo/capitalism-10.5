# Generated by Django 3.2.9 on 2022-02-13 16:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('economy', '0017_remove_commodity_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='commodity',
            name='simulation',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='economy.simulation'),
        ),
    ]
