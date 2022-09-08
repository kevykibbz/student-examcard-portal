
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
    path('site/contact',views.siteContact,name='site contact'),
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
]