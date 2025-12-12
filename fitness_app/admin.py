from django.contrib import admin
from.models import Fitness_Asessment   
from .models import Centre 
from .models import Facilities 
from .models import Staff 
from.models import Member 
from.models import Enrollment 
from.models import Class 

admin.site.register(Centre)
admin.site.register(Staff)
admin.site.register(Member)
admin.site.register(Enrollment) 
admin.site.register(Facilities) 



# Register your models here.
