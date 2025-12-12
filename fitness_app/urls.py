

from django.contrib import admin
from django.urls import path 
from.views import Allcentres,show_members,show_centre,Centre_classes,get_centre_classes
from .import views
urlpatterns = [
    path('admin/', admin.site.urls), 
      
    path('allcentres/',views.Allcentres),
     path('allcentres/<int:id>/',views.Allcentres),
     path('members/',views.show_members) ,
     path('api/login-with-hms-token/', views.login_with_hms_token, name='login_with_hms_token'),




     path('Centres/',views.show_centre) ,
        path('Centres/<int:id>/facilities/',views.Centre_classes),
        path('Centres/<int:id>/classes/',views.get_centre_classes),
        path('login/hospital/', views.hospital_login, name='hospital-login'),
path('callback/hospital/', views.hospital_callback, name='hospital-callback'),


   
    


]

