# Generated by Django 3.2.9 on 2022-09-09 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0006_auto_20220909_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursemodel',
            name='fee',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
