import dataclasses
from django.shortcuts import render
from manager.decorators import unauthenticated_user,allowed_users
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import *
from django.contrib.auth.models import User,Group,Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render,get_object_or_404
from django.views.generic import View
from django.template.loader import get_template
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse,HttpResponse,HttpResponseBadRequest
from installation.models import SiteConstants
from .forms import *
from django.core.paginator import Paginator
from django.contrib.sites.shortcuts import get_current_site
from .addons import send_email,getSiteData
import json
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.humanize.templatetags.humanize import intcomma
from django import template
import math
from django.utils.crypto import get_random_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.templatetags.static import static
from installation.models import SiteConstants
import re
from six.moves import urllib
from django.contrib.auth.hashers import make_password
import environ
env=environ.Env()
environ.Env.read_env()
from xhtml2pdf import pisa


#Login
@method_decorator(unauthenticated_user,name='dispatch')
class Login(View):
    def get(self,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        form=UserLoginForm()
        data={
            'title':'Login',
            'obj':obj,
            'data':request.user,
            'form':form,
            'login':True,
        }
        return render(request,'panel/login.html',context=data)
    def post(self,request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            key=request.POST['username']
            password=request.POST['password']
            if key:
                if password:
                    regex=re.compile(r'([A-Za-z0-9+[.-_]])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
                    if re.fullmatch(regex,key):
                        #email address
                        if User.objects.filter(email=key).exists():
                            data=User.objects.get(email=key)
                            user=authenticate(username=data.username,password=password)
                        else:
                            form_errors={"username": ["Invalid email address."]}
                            return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")
                    else:
                        #username
                        if User.objects.filter(username=key).exists():
                            user=authenticate(username=key,password=password)
                        else:
                            form_errors={"username": ["Invalid username."]}
                            return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")
                        
                    if user is not None:
                        if 'remember' in request.POST:
                           request.session.set_expiry(1209600) #two weeeks
                        else:
                           request.session.set_expiry(0) 
                        login(request,user)
                        return JsonResponse({'valid':True,'feedback':'success:Login Successfully.'},content_type="application/json")
                    form_errors={"password": ["Password is incorrect."]}
                    return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")
                else:
                    form_errors={"password": ["Password is required."]}
                    return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")
            else:
                form_errors={"username": ["Username/Email Address is required."]}
                return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")

#logout
def user_logout(request):
    logout(request)
    return redirect('/accounts/login')

#screenLock
def screenLock(request,username):
    logout(request)
    return redirect(f'/unlock/screen/{username}')

#screenUnlock
def screenUnlock(request,username):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    try:
        data=User.objects.get(username__exact=username)
        data={
            'title':'Screen Unlock',
            'obj':obj,
            'data':data,
        }
        return render(request,'panel/screen_unlock.html',context=data)       
    except User.DoesNotExist:
        data={
                'title':'Error | Page Not Found',
                'obj':obj
        }
        return render(request,'panel/404.html',context=data,status=404)

#siteContact
@login_required(login_url='accounts/login/')
@allowed_users(allowed_roles=['admins'])
def siteContact(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        instance_data=SiteConstants.objects.all().first()
        form=AddressConfigForm(request.POST or None , instance=instance_data)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')

#siteWorking
@login_required(login_url='accounts/login/')
@allowed_users(allowed_roles=['admins'])
def siteWorking(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        instance_data=SiteConstants.objects.all().first()
        form=WorkingConfigForm(request.POST, request.FILES or None , instance=instance_data)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')


#siteSocial
@login_required(login_url='accounts/login/')
@allowed_users(allowed_roles=['admins'])
def siteSocial(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        instance_data=SiteConstants.objects.all().first()
        form=UserSocialForm(request.POST or None , instance=instance_data)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')

# Create your views here.
def home(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data={
        'title':f'{request.user.get_full_name()} Dashboard',
        'obj':obj,
        'data':request.user,
    }
    return render(request,'panel/index.html',context=data)


#ProfileView
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
class ProfileView(View):
    def get(self,request,username):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user = get_object_or_404(User,username=username)
        form=CurrentLoggedInUserProfileChangeForm(request.POST or None,instance=user)
        eform=CurrentExtUserProfileChangeForm(request.POST or None,instance=user.extendedauthuser)
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        passform=UserPasswordChangeForm()
        profileform=ProfilePicForm()
        data={
            'title':f'Edit profile | {user.get_full_name()}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'eform':eform,
            'count':count,
            'messages':messages,
            'editor':user,
            'passform':passform,
            'profileform':profileform
        }
        return render(request,'panel/profile.html',context=data)
    def post(self,request,username,*args ,**kwargs):
        user=User.objects.get(username__exact=username)
        form=CurrentLoggedInUserProfileChangeForm(request.POST or None,instance=user)
        eform=CurrentExtUserProfileChangeForm(request.POST,request.FILES or None,instance=user.extendedauthuser)
        if form.is_valid() and eform.is_valid():
            form.save()
            eform.save()
            return JsonResponse({'valid':True,'message':'Profile updated successfully.','profile_pic':True},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors,'eform_errors':eform.errors,},content_type='application/json')



#passwordChange
@login_required(login_url='/accounts/login')
def passwordChange(request,username):
    if request.method=='POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        passform=UserPasswordChangeForm(request.POST or None,instance=request.user)
        if passform.is_valid():
            user=User.objects.get(username__exact=request.user.username)
            user.password=make_password(passform.cleaned_data.get('password1'))
            user.save()
            update_session_auth_hash(request,request.user)
            return JsonResponse({'valid':True,'message':'Password changed successfully'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':passform.errors},content_type='application/json')



#profile pic
@login_required(login_url='/accounts/login')
def profilePic(request):
    if request.method=='POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form=ProfilePicForm(request.POST,request.FILES or None,instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'profile picture changed successfully'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')


#General
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class General(View):
    def get(self,request):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        form1=SiteForm(instance=obj)
        form2=AddressConfigForm(instance=obj)
        form3=UserSocialForm(instance=obj)
        form4=WorkingConfigForm(instance=obj)
        data={
            'title':'General site settings',
            'obj':obj,
            'data':request.user,
            'messages':messages,
            'count':count,
            'form1':form1,
            'form2':form2,
            'form3':form3,
            'form4':form4,
        }
        return render(request,'panel/general.html',context=data) 
    def post(self,request,*args , **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            instance_data=SiteConstants.objects.all().first()
            form=SiteForm(request.POST,request.FILES or None , instance=instance_data)
            if form.is_valid():
                form.save()
                return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')


def download(request, *args, **kwargs):
    pk = kwargs.get('pk')
    customer = get_object_or_404(User,pk=pk)
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    template_path = 'panel/pdf2.html'
    context={'obj':obj,'customer':customer,'data':request.user}

    #Create a django response object and specify content_type as pdf
    response = HttpResponse(content_type = 'application/pdf')
    # response['Content-Disposition'] = 'attachment; filename = "report.pdf"'
    
    #find the template and render it
    template = get_template(template_path)
    html = template.render(context)

    #create pdf
    pisa_status = pisa.CreatePDF(
        html, dest = response
    )

    #if error then show some funny view
    if pisa_status.err:
        return HttpResponse("we had some errors<pre>" + html + "<pre>")
    return response    

def examCard(request):
    obj=SiteConstants.objects.count()
    if obj == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data={
        'title':'Exam Card Preview',
        'obj':obj,
        'data':request.user,
    }
    return render(request,'panel/examcard.html',context=data) 