# Generated by Django 3.2 on 2021-04-30 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20210430_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='delta',
            field=models.FloatField(),
        ),
    ]
