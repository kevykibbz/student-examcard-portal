from django.shortcuts import render
from .forms import *
from django.views.generic import View
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from manager.tokens import create_token
from django.contrib.sites.shortcuts import get_current_site
from  django.contrib.auth.models import Group
from manager.addons import send_email,getSiteData,sociallinks
from django.core.cache import cache
from django.contrib.sites.models import Site
# Create your views here.

def installation(request):
	return render(request,'installation/installation.html',{'title':'Site Installation | Powered By DevMe'})



class InstallationView(View):
	def get(self,request, *args, **kwargs):
		userform=AdminRegisterForm()
		extendedForm=ExtendedAdminRegisterForm()
		siteconstantform=SiteConfigForm()
		main=SubForm()
		count=ExtendedAdmin.objects.count()
		data={'userform':userform,'extendedForm':extendedForm,'siteconstantform':siteconstantform,'main':main,'count':count}	
		return render(request,'installation/installation_user_register.html',context=data)
	def post(self,request, *args, **kwargs):
		userform=AdminRegisterForm(request.POST or None)
		extendedForm=ExtendedAdminRegisterForm(request.POST or None)
		siteconstantform=SiteConfigForm(request.POST or None)
		main=SubForm(request.POST or None)
		if userform.is_valid() and extendedForm.is_valid() and siteconstantform.is_valid() and main.is_valid():
			user=userform.save(commit=False)
			user.is_superuser=True
			user.is_staff=True
			user.save()
			if not Group.objects.filter(name='admins').exists():
				group=Group.objects.create(name='admins')
				group.user_set.add(user)
				group.save()
			else:
				group=Group.objects.get(name__icontains='admins')
				group.user_set.add(user)
				group.save()
			extended=extendedForm.save(commit=False)
			extended.user=user
			extended.initials=userform.cleaned_data.get('first_name')[0].upper()+userform.cleaned_data.get('last_name')[0].upper()
			extended.social_links=sociallinks()
			extended.role='Admin'
			extended.save()
			lastdata=siteconstantform.save(commit=False)
			lastdata.user=user
			lastdata.save()
			admindata=main.save(commit=False)
			admindata.user=user
			admindata.is_installed=True
			Site.objects.create(name=siteconstantform.cleaned_data.get('site_name'),domain=siteconstantform.cleaned_data.get('site_url'))
			admindata.save()
			return JsonResponse({'valid':True,'message':'data saved'},content_type='application/json')
		else:
			return JsonResponse({'valid':False,'main_errors':main.errors,'userform_errors':userform.errors,'extendedForm_errors':extendedForm.errors,'siteconstantform_errors':siteconstantform.errors},content_type='application/json')
