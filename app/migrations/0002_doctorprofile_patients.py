# Generated by Django 5.1.1 on 2024-09-19 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctorprofile',
            name='patients',
            field=models.ManyToManyField(blank=True, to='app.patientprofile'),
        ),
    ]
