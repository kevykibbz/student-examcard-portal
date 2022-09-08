from django.http import HttpResponse
from django.shortcuts import redirect, render
from installation.models import SiteConstants
def unauthenticated_user(view_func):
    def wrapper_func(request, *args , **kwrags):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('/panel')
        else:
            return view_func(request, *args , **kwrags)
    return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args , **kwrags):
            group=None
            if request.user.groups.exists():
                group=request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request, *args , **kwrags)
            else:
                obj=SiteConstants.objects.all()[0]
                return render(request,'manager/403.html',{'title':'Access Forbidden','obj':obj})
        return wrapper_func
    return decorator


