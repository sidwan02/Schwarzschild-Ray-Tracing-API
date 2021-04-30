# Generated by Django 3.2 on 2021-04-30 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RayTracing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('delta0', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='position',
            name='delta',
            field=models.FloatField(default='0'),
        ),
    ]
