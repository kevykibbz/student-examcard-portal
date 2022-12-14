# Generated by Django 3.2.9 on 2022-09-08 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconstants',
            name='stamp',
            field=models.ImageField(blank=True, default='stamp/stamp.png', null=True, upload_to='stamp/'),
        ),
        migrations.AlterField(
            model_name='siteconstants',
            name='description',
            field=models.TextField(blank=True, default='sample site description', null=True),
        ),
        migrations.AlterField(
            model_name='siteconstants',
            name='favicon',
            field=models.ImageField(blank=True, default='logos/favicon.ico', null=True, upload_to='logos/'),
        ),
        migrations.AlterField(
            model_name='siteconstants',
            name='key_words',
            field=models.TextField(blank=True, default='illuminate', null=True),
        ),
        migrations.AlterField(
            model_name='siteconstants',
            name='site_email',
            field=models.CharField(blank=True, default='illuminate@gmail.com', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='siteconstants',
            name='site_name',
            field=models.CharField(blank=True, default='Illuminate', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='siteconstants',
            name='site_url',
            field=models.URLField(blank=True, default='https://illuminate.com', null=True),
        ),
        migrations.AlterField(
            model_name='siteconstants',
            name='theme_color',
            field=models.CharField(blank=True, default='#51be78', max_length=100, null=True),
        ),
    ]
