# Generated by Django 3.2 on 2021-05-02 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_position_delta'),
    ]

    operations = [
        migrations.AddField(
            model_name='raytracing',
            name='z',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
