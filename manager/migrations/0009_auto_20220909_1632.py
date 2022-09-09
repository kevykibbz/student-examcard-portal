# Generated by Django 3.2.9 on 2022-09-09 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0008_auto_20220909_1611'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='extendedauthuser',
            name='fee',
        ),
        migrations.AddField(
            model_name='extendedauthuser',
            name='fee_balance',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='extendedauthuser',
            name='paid_fee',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
