from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.utils.timezone import now
import environ
env=environ.Env()
environ.Env.read_env()

# Create your models here.

class SiteConstants(models.Model):
    user=models.OneToOneField(User,primary_key=True,on_delete=models.CASCADE)
    site_name=models.CharField(null=True,blank=True,max_length=100,default=env('SITE_NAME'))
    site_email=models.CharField(null=True,blank=True,max_length=100,default=env('SITE_EMAIL'))
    site_email2=models.CharField(null=True,blank=True,max_length=100,default=env('SITE_EMAIL2'))
    theme_color=models.CharField(null=True,blank=True,max_length=100,default=env('THEME_COLOR'))
    site_url=models.URLField(null=True,blank=True,default=env('SITE_URL'))
    description=models.TextField(null=True,blank=True,default=env('SITE_DESCRIPTION'))
    key_words=models.TextField(null=True,blank=True,default=env('SITE_KEYWORDS'))
    address=models.CharField(null=True,blank=True,max_length=250,default=env('SITE_ADDRESS'))
    location=models.CharField(null=True,blank=True,max_length=250,default=env('SITE_LOCATION'))
    phone=PhoneNumberField(null=True,blank=True,verbose_name='phone',unique=False,default=env('SITE_PHONE1'))
    working_days=models.CharField(null=True,blank=True,max_length=250,default="mon-fri")
    site_content=models.CharField(null=True,blank=True,max_length=250)
    working_hours=models.CharField(null=True,blank=True,max_length=250,default="8am-10pm")
    closed_days=models.CharField(null=True,blank=True,max_length=250,default="sun")
    special_days=models.CharField(null=True,blank=True,max_length=250,default="sat & holidays")
    special_hours=models.CharField(null=True,blank=True,max_length=250,default="sat & holidays")
    facebook=models.URLField(null=True,blank=True,max_length=250,default=env('FACEBOOK_LINK'))
    twitter=models.URLField(null=True,blank=True,max_length=250,default=env('TWITTER_LINK'))
    instagram=models.URLField(null=True,blank=True,max_length=250,default=env('INSTAGRAM_LINK'))
    whatsapp=models.URLField(null=True,blank=True,max_length=250,default=env('WHATSAPP_LINK'))
    linkedin=models.URLField(null=True,blank=True,max_length=250,default=env('LINKEDIN_LINK'))
    youtube=models.URLField(null=True,blank=True,max_length=250,default=env('YOUTUBE_LINK'))
    favicon=models.ImageField(null=True,blank=True,upload_to='logos/',default="logos/favicon.ico")
    icon_180=models.ImageField(null=True,blank=True,upload_to='logos/',default="favicon-180x180.png")
    icon_32=models.ImageField(null=True,blank=True,upload_to='logos/',default="favicon-32x32.png")
    icon_16=models.ImageField(null=True,blank=True,upload_to='logos/',default="favicon-16x16.png")
    created_on=models.DateTimeField(default=now)
    class Meta:
        db_table='site_constants'
        verbose_name_plural='site_constants'
    def __str__(self):
        return f'{self.user.username} site constants'
