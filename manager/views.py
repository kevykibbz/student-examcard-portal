import dataclasses
from django.shortcuts import render
from manager.decorators import unauthenticated_user,allowed_users
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import *
from django.contrib.auth.models import User,Group,Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render,get_object_or_404,redirect
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
import environ
env=environ.Env()
environ.Env.read_env()
from xhtml2pdf import pisa

def generate_id():
    return get_random_string(6,'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKMNOPQRSTUVWXYZ0123456789')

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
        percent=int(request.user.extendedauthuser.paid_fee)/int(request.user.extendedauthuser.fee_balance)*100
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
            'profileform':profileform,
            'percent':percent,
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
    exams=ExamModel.objects.filter(user_id=request.user.pk).order_by('-id')
    latest=ExamModel.objects.filter(user_id=request.user.pk).first()
    stamp=CourseModel.objects.get(course_name=request.user.extendedauthuser.course_name)
    template_path = 'panel/pdf2.html'
    context={'exams':exams,'obj':obj,'customer':customer,'data':request.user,'latest':latest,'stamp':stamp}

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

#newStudent
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class newStudent(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        schools=SchoolModel.objects.all().order_by("-id")
        courses=CourseModel.objects.all().order_by("-id")
        form=users_registerForm()
        eform=EProfileForm()
        data={
            'title':'Add new student',
            'obj':obj,
            'data':request.user,
            'count':count,
            'messages':messages,
            'form':form,
            'eform':eform,
            'schools':schools,
            'courses':courses,
        }
        return render(request,'panel/add_student.html',context=data)
    def post(self,request):
        if  request.headers.get('x-requested-with') == 'XMLHttpRequest':
            uform=users_registerForm(request.POST or None)
            eform=EProfileForm(request.POST , request.FILES or None)
            if uform.is_valid() and  eform.is_valid():
                userme=uform.save(commit=False)
                userme.is_active = True
                userme.password=make_password('@'+uform.cleaned_data.get('username',None)+eform.cleaned_data.get('reg_no',None))
                userme.save()
                extended=eform.save(commit=False)
                courses=CourseModel.objects.get(course_name=eform.cleaned_data.get('course_name',None))
                extended.user=userme
                extended.role='Student'
                if 'is_cleared' in request.POST:
                    extended.is_cleared=True
                else:
                    extended.is_cleared=False
                extended.exam_id=generate_id()
                extended.fee_balance=courses.fee
                extended.initials=uform.cleaned_data.get('first_name')[0].upper()+uform.cleaned_data.get('last_name')[0].upper()
                extended.save()
                return JsonResponse({'valid':True,'message':'Student added successfully','profile_pic':request.user.extendedauthuser.profile_pic.url},content_type="application/json")
            else:
                return JsonResponse({'valid':False,'uform_errors':uform.errors,'eform_errors':eform.errors},content_type="application/json")


#courses
def courses(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data=CourseModel.objects.all().order_by("-id")
    paginator=Paginator(data,10)
    page_num=request.GET.get('page')
    courses=paginator.get_page(page_num)
    data={
        'title':'View All Courses',
        'obj':obj,
        'data':request.user,
        'courses':courses,
        'count':paginator.count
    }
    return render(request,'panel/courses.html',context=data)


#schools
def schools(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data=SchoolModel.objects.all().order_by("-id")
    paginator=Paginator(data,10)
    page_num=request.GET.get('page')
    schools=paginator.get_page(page_num)
    data={
        'title':'View All Schools',
        'obj':obj,
        'data':request.user,
        'schools':schools,
        'count':paginator.count
    }
    return render(request,'panel/schools.html',context=data)

#newSchool
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class newSchool(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        form=SchoolForm()
        data={
            'title':'Add School',
            'obj':obj,
            'data':request.user,
            'count':count,
            'messages':messages,
            'form':form,
        }
        return render(request,'panel/add_school.html',context=data)
    def post(self,request):
        if  request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form=SchoolForm(request.POST or None)
            if form.is_valid():
                usr=form.save(commit=False)
                usr.user_id=request.user.pk
                usr.save()
                return JsonResponse({'valid':True,'message':'New school added successfully'},content_type="application/json")
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},content_type="application/json")

#editSchool
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class editSchool(View):
    def get(self ,request,id):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=SchoolModel.objects.get(id=id)
        form=SchoolForm(instance=user)
        data={
            'title':f'Edit school | {user.school}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'school':user,
            'edit':True,
        }
        return render(request,'panel/add_school.html',context=data)

    def post(self,request,id,*args ,**kwargs):
        user=SchoolModel.objects.get(id=id)
        form=SchoolForm(request.POST or None,instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'School name updated successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#deleteSchool
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteSchool(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=SchoolModel.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'School name deleted successfully.','id':id},content_type='application/json')       
        except SchoolModel.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Item does not exist'},content_type='application/json')

#newCourse
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class newCourse(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        schools=SchoolModel.objects.all().order_by("-id")
        form=CourseForm()
        data={
            'title':'Add Course',
            'obj':obj,
            'data':request.user,
            'count':count,
            'messages':messages,
            'form':form,
            'schools':schools,
        }
        return render(request,'panel/add_course.html',context=data)
    def post(self,request):
        if  request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form=CourseForm(request.POST,request.FILES or None)
            if form.is_valid():
                usr=form.save(commit=False)
                usr.user_id=request.user.pk
                usr.save()
                return JsonResponse({'valid':True,'message':'Course added successfully'},content_type="application/json")
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},content_type="application/json")

#editCourse
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class editCourse(View):
    def get(self ,request,id):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=CourseModel.objects.get(id=id)
        schools=SchoolModel.objects.all().order_by("-id")
        form=CourseForm(instance=user)
        data={
            'title':f'Edit course | {user.course_name}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'school':user,
            'edit':True,
            'schools':schools,
        }
        return render(request,'panel/add_course.html',context=data)

    def post(self,request,id,*args ,**kwargs):
        user=CourseModel.objects.get(id=id)
        form=CourseForm(request.POST,request.FILES or None,instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'School name updated successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#deleteCourse
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteCourse(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=CourseModel.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Course name deleted successfully.','id':id},content_type='application/json')       
        except CourseModel.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Item does not exist'},content_type='application/json')



#semister
def semister(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data=SemModel.objects.all().order_by("-id")
    paginator=Paginator(data,20)
    page_num=request.GET.get('page')
    sems=paginator.get_page(page_num)
    data={
        'title':'View Semister Outline',
        'obj':obj,
        'data':request.user,
        'sems':sems,
        'count':paginator.count
    }
    return render(request,'panel/semister.html',context=data)

#newSem
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class newSem(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        schools=SchoolModel.objects.all().order_by("-id")
        courses=CourseModel.objects.all().order_by("-id")
        form=SemForm()
        data={
            'title':'New Semister Outline',
            'obj':obj,
            'data':request.user,
            'count':count,
            'messages':messages,
            'form':form,
            'schools':schools,
            'courses':courses,
        }
        return render(request,'panel/new_semister.html',context=data)
    def post(self,request):
        if  request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form=SemForm(request.POST or None)
            if form.is_valid():
                usr=form.save(commit=False)
                usr.user_id=request.user.pk
                usr.save()
                return JsonResponse({'valid':True,'message':'Outline added successfully'},content_type="application/json")
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},content_type="application/json")

#editOutline
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class editOutline(View):
    def get(self ,request,id):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=SemModel.objects.get(id=id)
        schools=SchoolModel.objects.all().order_by("-id")
        courses=CourseModel.objects.all().order_by("-id")
        form=SemForm(instance=user)
        data={
            'title':f'Edit semister outline | {user.course_name}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'school':user,
            'edit':True,
            'schools':schools,
            'courses':courses,
        }
        return render(request,'panel/new_semister.html',context=data)

    def post(self,request,id,*args ,**kwargs):
        user=SemModel.objects.get(id=id)
        form=SemForm(request.POST or None,instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'Semister outline  updated successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#deleteOutline
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteOutline(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=SemModel.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Semister outline  deleted successfully.','id':id},content_type='application/json')       
        except SemModel.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Item does not exist'},content_type='application/json')

#allStudents
def allStudents(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data=User.objects.filter(extendedauthuser__role='Student').order_by("-id")
    paginator=Paginator(data,20)
    page_num=request.GET.get('page')
    students=paginator.get_page(page_num)
    data={
        'title':'View all students',
        'obj':obj,
        'data':request.user,
        'students':students,
        'count':paginator.count
    }
    return render(request,'panel/students.html',context=data)


#editStudent
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class editStudent(View):
    def get(self ,request,id):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=User.objects.get(id=id)
        schools=SchoolModel.objects.all().order_by("-id")
        courses=CourseModel.objects.all().order_by("-id")
        form=CurrentLoggedInUserProfileChangeForm(instance=user)
        eform=EProfileForm(instance=user.extendedauthuser)  
        data={
            'title':f'Edit student | {user.get_full_name()}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'eform':eform,
            'school':user,
            'edit':True,
            'schools':schools,
            'courses':courses,
            'student':user,
        }
        return render(request,'panel/add_student.html',context=data)

    def post(self,request,id,*args ,**kwargs):
        user=User.objects.get(id=id)
        form=CurrentLoggedInUserProfileChangeForm(request.POST or None , instance=user)
        eform=EProfileForm(request.POST,request.FILES or None ,instance=user.extendedauthuser)             
        if form.is_valid() and eform.is_valid():
            form.save()
            usr=eform.save(commit=False)
            if 'is_cleared' in request.POST:
                usr.is_cleared=True
            else:
                usr.is_cleared=False
            usr.save()
            return JsonResponse({'valid':True,'message':'Student updated successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors,'eform_errors':eform.errors},content_type='application/json')

#deleteStudent
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteStudent(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=User.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Student deleted successfully.','id':id},content_type='application/json')       
        except User.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Item does not exist'},content_type='application/json')




#getCourses
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
class getCourses(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        if request.GET.get('year') and request.GET.get('sem'):
            try:
                courses=SemModel.objects.filter(year=request.GET.get('year'),sem=request.GET.get('sem'),school=request.user.extendedauthuser.school,course_name=request.user.extendedauthuser.course_name).order_by("-id")
                count=SemModel.objects.filter(year=request.GET.get('year'),sem=request.GET.get('sem'),school=request.user.extendedauthuser.school,course_name=request.user.extendedauthuser.course_name).count()
                data={
                        'title':'View all students',
                        'obj':obj,
                        'data':request.user,
                        'courses':courses,
                        'count':count
                    }
                return render(request,'panel/register_courses.html',context=data)
            except SemModel.DoesNotExist:
                data={
                    'title':'Error | Page Not Found',
                    'obj':obj
                    }
                return render(request,'panel/404.html',context=data,status=404)
        else:
            return redirect('/dashboard')
    def post(self,request):
        form=NominalRollForm(request.POST or None , instance=request.user.extendedauthuser)
        if form.is_valid():
            ids=json.loads(request.POST.get('course_ids',None))
            usr=form.save(commit=False)
            usr.registered_courses=ids
            usr.save()
            if not ExamModel.objects.filter(user_id=request.user.pk).exists():
                for id in ids['arr']:
                    courses=SemModel.objects.get(id=id)
                    obj=ExamModel.objects.create(user_id=request.user.pk,academic_year=courses.academic_year,school=request.user.extendedauthuser.school,year=courses.year,sem=courses.sem,course_code=courses.course_code,course_name=courses.course_name,course_title=courses.course_title)
                    obj.save()
                return JsonResponse({'valid':True,'message':'Courses registered successfuly.'},content_type='application/json')
            else:
                usr=ExamModel.objects.filter(user_id=request.user.pk).first()
                for id in ids['arr']:
                    courses=SemModel.objects.get(id=id)
                    usr.user_id=request.user.pk
                    usr.academic_year=courses.academic_year
                    usr.year=courses.year
                    usr.sem=courses.sem
                    usr.course_code=courses.course_code
                    usr.course_name=courses.course_name
                    usr.course_title=courses.course_title
                    usr.school=request.user.extendedauthuser.school
                    usr.save()
                return JsonResponse({'valid':True,'message':'Courses registered successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#registeredCourses
def registeredCourses(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    exams=ExamModel.objects.filter(user_id=request.user.pk).order_by('-id')
    count=ExamModel.objects.filter(user_id=request.user.pk).count()
    data={
        'title':'View all registered courses',
        'obj':obj,
        'data':request.user,
        'exams':exams,
        'count':count
    }
    return render(request,'panel/registered_courses.html',context=data)

#deleteRegisteredCourse
@login_required(login_url='/accounts/login')
def deleteRegisteredCourse(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=ExamModel.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Item deleted successfully.','id':id},content_type='application/json')       
        except ExamModel.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Item does not exist'},content_type='application/json')

#prepExamCard
def prepExamCard(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    exams=ExamModel.objects.filter(user_id=request.user.pk).order_by('-id')
    count=ExamModel.objects.filter(user_id=request.user.pk).count()
    percent=int(request.user.extendedauthuser.paid_fee)/int(request.user.extendedauthuser.fee_balance)*100
    data={
        'title':'Preparing for exam card download',
        'obj':obj,
        'data':request.user,
        'exams':exams,
        'count':count,
        'percent':percent,
    }
    return render(request,'panel/prep_examcard.html',context=data)