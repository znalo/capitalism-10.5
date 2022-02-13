# Generated by Django 3.2.9 on 2022-02-13 16:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('economy', '0019_alter_simulation_current_time_stamp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockowner',
            name='user',
        ),
        migrations.AddField(
            model_name='stockowner',
            name='simulation',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='economy.simulation'),
        ),
    ]
