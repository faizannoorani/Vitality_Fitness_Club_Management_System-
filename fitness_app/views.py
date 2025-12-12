from django.shortcuts import render 
from django.http import JsonResponse 
from .models import Centre 
from .models import Facilities 
from .models import Staff 
from.models import Member 

from django.contrib.auth import authenticate 
from rest_framework.response import Response

from.models import Enrollment 
from.models import Class 
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.authentication import BasicAuthentication

from.models import Fitness_Asessment  
from rest_framework  import status 
from.serializers import SignupSerializer

from.serializers import CentreGetSerializer,CentrePOSTSerializer,Centre_user_serializer,CentreuserSerializer
from .serializers import CentreclassesSerializer
from rest_framework.decorators import api_view 


from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from .models import Centre
from .serializers import CentreGetSerializer, CentrePOSTSerializer,MembergetSerializer

from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from .models import Centre
from .serializers import CentreGetSerializer, CentrePOSTSerializer








import requests
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse 
from django.contrib.auth import get_user_model


# Step 1: Redirect user to HMS authorize endpoint (for browser flow)





User = get_user_model()
HMS_URL = "http://127.0.0.1:8001"  # HMS URL

@api_view(['POST'])
def login_with_hms_token(request):
    """
    Accepts HMS access token, verifies it, and logs in user in FMS.
    """
    hms_token = request.data.get('hms_token')
    if not hms_token:
        return Response({"error": "HMS token required"}, status=status.HTTP_400_BAD_REQUEST)

    # Call HMS user-info endpoint
    try:
        hms_response = requests.get(f"{HMS_URL}/api/user-info/", headers={
            "Authorization": f"Bearer {hms_token}"
        })
    except requests.exceptions.RequestException:
        return Response({"error": "Cannot connect to HMS"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if hms_response.status_code != 200:
        return Response({"error": "HMS token invalid"}, status=status.HTTP_401_UNAUTHORIZED)

    user_data = hms_response.json()
    username = user_data.username

    # Get or create local user in FMS
    user, created = User.objects.get_or_create(username=username, defaults={
        'email': user_data.get('email', ''),
        'first_name': user_data.get('first_name', ''),
        'last_name': user_data.get('last_name', ''),
    })

    # Generate FMS JWT token for the user
    refresh = RefreshToken.for_user(user)

    return Response({
        "fms_access": str(refresh.access_token),
        "fms_refresh": str(refresh),
        "created": created
    })
def hospital_login(request):
    auth_url = f"{settings.SOCIAL_AUTH_HOSPITAL_AUTHORIZATION_URL}?response_type=code&client_id={settings.SOCIAL_AUTH_HOSPITAL_KEY}&redirect_uri=http://localhost:8002/callback/hospital/&scope={' '.join(settings.SOCIAL_AUTH_HOSPITAL_SCOPE)}"
    return redirect(auth_url)


# Step 2: Callback endpoint after HMS authorization
def hospital_callback(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({"error": "No code provided"}, status=400)

    # Exchange code for token
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:8002/callback/hospital/',
        'client_id': settings.SOCIAL_AUTH_HOSPITAL_KEY,
        'client_secret': settings.SOCIAL_AUTH_HOSPITAL_SECRET
    }

    token_response = requests.post(settings.SOCIAL_AUTH_HOSPITAL_ACCESS_TOKEN_URL, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')

    if not access_token:
        return JsonResponse({"error": "Failed to get access token"}, status=400)

    # Optional: fetch user info from HMS
    user_info_response = requests.get(
        settings.SOCIAL_AUTH_HOSPITAL_USER_INFO_URL,
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_info = user_info_response.json()
    username = user_info.get('username') or user_info.get('email')

    # Create or get user in FMS
    user, created = User.objects.get_or_create(username=username)
    login(request, user)  # Log user into FMS

    return JsonResponse({
        "message": "Login successful",
        "username": username,
        "access_token": access_token
    })




@api_view(['GET', 'POST','PUT','PATCH','DELETE'])
def Allcentres(request, id=None):
    if request.method == 'GET':
        if id is not None:
            try:
                c = Centre.objects.get(id=id)
                ser = CentreGetSerializer(c)
                return JsonResponse(ser.data, status=status.HTTP_200_OK, safe=False)
            except Centre.DoesNotExist:
                return JsonResponse({"error": "Centre not exists"}, status=status.HTTP_404_NOT_FOUND)
        else:
            c = Centre.objects.all()
            ser = CentreGetSerializer(c, many=True)
            return JsonResponse(ser.data, status=status.HTTP_200_OK, safe=False)

    elif request.method == 'POST':
        ser = CentrePOSTSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return JsonResponse(ser.data, safe=False, status=status.HTTP_201_CREATED)
        return JsonResponse(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    


    elif request.method=='PUT':
        c=Centre.objects.get(id=id) 
        ser=CentrePOSTSerializer(c) 
        if ser.is_valid():
            ser.save()
            return JsonResponse(ser.data,safe=False,status=status.HTTP_201_CREATED) 

        return JsonResponse(ser.errors,status=status.HTTP_400_BAD_REQUEST) 
    

    elif request.method=='PATCH':
        c=Centre.objects.get(id=id) 
        ser=CentrePOSTSerializer(c) 
        if ser.is_valid():
            ser.save()
            return JsonResponse(ser.data,safe=False,status=status.HTTP_201_CREATED) 

        return JsonResponse(ser.errors,status=status.HTTP_400_BAD_REQUEST) 
    

    elif request.method=='DELETE':

        try:
          c=Centre.objects.get(id=id) 
          c.delete()

        except Centre.DoesNotExist:
            return JsonResponse({"error":"centre does not exist"},status=status.HTTP_400_BAD_REQUEST) 
        
@api_view(['GET']) 
def show_members(request):  

  m=Member.objects.all() 
  ser=MembergetSerializer(m,many=True) 
  return JsonResponse(ser.data,status=status.HTTP_202_ACCEPTED)  




## Memebrs Apis onward 










@api_view(['GET'])
def show_centre(request,id=None ): 

    if request.method=='GET':
        if id is not None: 
            c=Centre.objects.get(id=id) 
            ser=Centre_user_serializer(c) 
            return JsonResponse(ser.data,status=status.HTTP_200_OK) 


        else:
          c=Centre.objects.all()
          ser=Centre_user_serializer(ser,many=True) 
          return JsonResponse(ser.data,status=status.HTTP_200_OK) 
        

@api_view(['GET'])
def Centre_classes(request,id=None): 
    if request.method =='GET':
        c=Centre.objects.prefetch_related('Facilities').get(id=id)
        ser=CentreuserSerializer(c) 
        return JsonResponse(ser.data,status=status.HTTP_200_OK)  
    


@api_view(['GET'])
def get_centre_classes(request,id=None): 
    c=Centre.objects.prefetch_related('class').get(id=id) 
    ser=CentreclassesSerializer(c,many=True) 
    return JsonResponse(ser.data,safe=False,status=status.HTTP_200_OK)   







    





            
       

    

    

