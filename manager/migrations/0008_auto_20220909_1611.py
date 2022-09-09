# Generated by Django 3.2.9 on 2022-09-09 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0007_coursemodel_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='extendedauthuser',
            name='course_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='extendedauthuser',
            name='school',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='coursemodel',
            name='fee',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='extendedauthuser',
            name='exam_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
