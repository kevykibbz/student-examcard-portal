
from django.urls import path
from django import views
from . import views
from .views import *
from django.contrib.auth import views as auth_views
urlpatterns=[
    path('',Login.as_view(),name='dashboard'),
    path('accounts/login',Login.as_view(),name='dashboard'),
    path('dashboard',views.home,name='home'),
    path('accounts/logout',views.user_logout,name='logout'),
    path('lock/screen/<str:username>',views.screenLock,name='lock screen'),
    path('unlock/screen/<str:username>',views.screenUnlock,name='unlock screen'),
    path('<str:username>',ProfileView.as_view(),name='profile'),
    path('accounts/register',newStudent.as_view(),name='new student'),
    path('add/school',newSchool.as_view(),name='new school'),
    path('add/courses',newCourse.as_view(),name='new course'),
    path('register/semister',newSem.as_view(),name='new semister'),
    path('site/contact',views.siteContact,name='site contact'),
    path('all/schools',views.schools,name='schools'),
    path('all/courses',views.courses,name='courses'),
    path('site/working/days',views.siteWorking,name='site working days'),
    path('site/social/links',views.siteSocial,name='site social links'),
    path('general/site/settings',General.as_view(),name='general'),
    path('download/exam/card/<pk>',views.download, name='download exam card'),
    path('exam/card/',views.examCard, name='exam card'),
    path('user/password/change/<str:username>',views.passwordChange,name='user password change'),
    path('user/profile/picture/change',views.profilePic,name='user profile picture change'),
    path('accounts/reset/password',auth_views.PasswordResetView.as_view(form_class=UserResetPassword,template_name='panel/password_reset.html'),name='reset_password'),
    path('accounts/reset/password/done',auth_views.PasswordResetDoneView.as_view(template_name='panel/password_reset_done.html'),name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name='panel/password_reset_confirm.html'),name='password_reset_confirm'),
    path('accounts/reset/password/complete',auth_views.PasswordResetCompleteView.as_view(template_name='panel/password_reset_complete.html'),name='password_reset_complete'),


    path('edit/school/<int:id>',editSchool.as_view(),name='edit school'),
    path('delete/school/<int:id>',views.deleteSchool,name='delete school'), 
    path('edit/course/<int:id>',editCourse.as_view(),name='edit course'),
    path('delete/course/<int:id>',views.deleteCourse,name='delete course'),
    path('view/semister/outline',views.semister,name='semister'),

    path('edit/semister/outline/<int:id>',editOutline.as_view(),name='edit outline'),
    path('delete/semister/outline/<int:id>',views.deleteOutline,name='delete outline'), 
    path('view/students',views.allStudents,name='students'), 

    path('edit/student/<int:id>',editStudent.as_view(),name='edit student'),
    path('delete/student/<int:id>',views.deleteStudent,name='delete student'), 
    path('get/courses',getCourses.as_view(),name='get courses'), 

    path('view/registered/courses',views.registeredCourses,name='registered courses'), 

    path('drop/course/<int:id>',views.deleteRegisteredCourse,name='delete registered course'), 
    path('exam/card',views.prepExamCard,name='prepare exam card'), 

]