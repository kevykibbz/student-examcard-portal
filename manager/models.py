from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from manager.addons import send_email
import random
import jsonfield
from installation.models import SiteConstants
from django.utils.crypto import get_random_string
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Max
from django.utils.translation import gettext_lazy as _
import environ
env=environ.Env()
environ.Env.read_env()

class ExtendedAdmin(models.Model):
    user=models.OneToOneField(User,primary_key=True,on_delete=models.CASCADE)
    location=models.CharField(null=True,blank=True,max_length=100)
    main=models.BooleanField(default=False)
    is_installed=models.BooleanField(default=False)

    class Meta:
        db_table='extended_admin'
        verbose_name_plural='extended_admins'

    def __str__(self):
        return f'{self.user.username} site extended admin'


        
#generate random
def generate_id():
    return get_random_string(6,'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKMNOPQRSTUVWXYZ0123456789')




@receiver(post_save, sender=ExtendedAdmin)
def send_installation_email(sender, instance, created, **kwargs):
    if created:
        if instance.is_installed:
            #site is installed
            subject='Congragulations:Site installed successfully.'
            email=instance.user.email
            message={
                        'user':instance.user,
                        'site_name':instance.user.siteconstants.site_name,
                        'site_url':instance.user.siteconstants.site_url
                    }
            template='emails/installation.html'
            send_email(subject,email,message,template)





def bgcolor():
    hex_digits=['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    digit_array=[]
    for i in range(6):
        digits=hex_digits[random.randint(0,15)]
        digit_array.append(digits)
    joined_digits=''.join(digit_array)
    color='#'+joined_digits
    return color





options=[
            ('employee','Employee'),
            ('admins','Admin'),
        ]
class ExtendedAuthUser(models.Model):
    user=models.OneToOneField(User,primary_key=True,on_delete=models.CASCADE)
    phone=PhoneNumberField(null=True,blank=True,verbose_name='phone',unique=True,max_length=13)
    initials=models.CharField(max_length=10,blank=True,null=True)
    bgcolor=models.CharField(max_length=10,blank=True,null=True,default=bgcolor)
    company=models.CharField(max_length=100,null=True,blank=True,default=env('SITE_NAME'))
    profile_pic=models.ImageField(upload_to='profiles/',null=True,blank=True,default="placeholder.jpg")
    role=models.CharField(choices=options,max_length=200,null=True,blank=True)
    bio=models.TextField(null=True,blank=True)
    created_on=models.DateTimeField(default=now)
    class Meta:
        db_table='extended_auth_user'
        verbose_name_plural='extended_auth_users'
        permissions=(
            ("can_view","Can view"),
            ("can_edit","Can edit"),
            ("can_see_invoice","Can see invoice"),
        )
    def __str__(self)->str:
        return f'{self.user.username} extended auth profile'




#generate random
def generate_serial():
    return get_random_string(12,'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKMNOPQRSTUVWXYZ0123456789')
 

 




class ContactModel(models.Model):
    name=models.CharField(max_length=100,blank=True,null=True)
    phone=PhoneNumberField(null=True,blank=True,verbose_name='phone',max_length=13)
    subject=models.CharField(max_length=100,null=True,blank=True)
    email=models.CharField(max_length=100,blank=True,null=True)
    initials=models.CharField(max_length=10,blank=True,null=True)
    bgcolor=models.CharField(max_length=10,blank=True,null=True,default=bgcolor)
    is_read=models.BooleanField(default=False,blank=True,null=True)
    message=models.TextField(blank=True,null=True)
    reply=models.TextField(blank=True,null=True)
    created_on=models.DateTimeField(default=now)
    class Meta:
        db_table='contact_tbl'
        verbose_name_plural='contact_tbl'
    def __str__(self)->str:
        return f'{self.name} contact message'




@receiver(post_save, sender=ContactModel)
def send_contact_email(sender, instance, created, **kwargs):
    if created and instance.message:
        obj=SiteConstants.objects.all()[0]
        subject='Message received.'
        email=instance.email
        message={
                    'user':instance.name,
                    'site_name':obj.site_name,
                    'site_url':obj.site_url,
                    'address':obj.address,
                    'phone':obj.phone
                }
        template='emails/contact.html'
        send_email(subject,email,message,template)