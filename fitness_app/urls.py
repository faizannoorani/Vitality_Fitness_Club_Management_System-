

from django.contrib import admin
from django.urls import path 
 
from . import views
urlpatterns = [
    
    path('admin/', admin.site.urls), 
      
    path('allcentres/',views.Allcentres),
     path('allcentres/<int:id>/',views.Allcentres),
     path('create/centre',views.Allcentres) ,
     path('update/centre/<int:id>',views.Allcentres),
     path('update/fully/centre/<int:id>',views.Allcentres),
     path('members/',views.show_members) ,
     path('api/login-with-hms-token/', views.login_with_hms_token, name='login_with_hms_token'),
     path('Centres/',views.show_centre) ,
    path('Centres/<int:id>/facilities/',views.Centre_classes),
    path('Centres/<int:id>/classes/',views.get_centre_classes),
  
path('staff/<int:id>/centre/',views.get_staff_by_centre), 
path('create/staff',views.staff_data) ,
path('get/allstaff/',views.staff_detail),
  path('staff/byrole/',views.get_staff_by_role), 
  path('facilities/classes/<int:id>',views.get_classes_by_facility),
path('create/facility',views.create_facility),
path('classes/<int:id>/',views.get_classes),
path('classes/',views.get_classes),
path('create/class',views.create_class),

path('login/',views.login),
path('signup/',views.Signup_fun),
path('verify-otp/<int:id>/',views.verifyOTP) 




    
    


]

