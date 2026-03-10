


from functools import wraps
from rest_framework.response import Response
from rest_framework import status 
from django.contrib.auth.models import User 

from .models import User_role

from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission  



def member_required(view_func):
    @wraps(view_func)  
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return Response ({'error':'Unauthorized user ,first signup '},status=status.HTTP_400_BAD_REQUEST) 
        
        
            
        elif request.user.user_role!='member':
            return Response({"error":"this api only for members "},status=status.HTTP_401_UNAUTHORIZED) 
        elif request.user.user_role=='member': 
         
           return view_func(request, *args, **kwargs)
    return _wrapped_view 
        

