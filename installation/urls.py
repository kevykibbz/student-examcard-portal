from django.urls import path
from django import views
from . import views
from .views import *
urlpatterns=[
   path('',views.installation,name='installation'),
   path('installation/start',InstallationView.as_view(),name='installation start')
]

