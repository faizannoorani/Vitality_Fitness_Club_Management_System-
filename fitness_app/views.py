

from Fitness_Club.settings import HMS_URL
from rest_framework.permissions import IsAuthenticated
from .models import Staff, Facilities,OTP
from .models import Member 
from .models import Class ,Signup,Login
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    Centre_user_serializer, CentreuserSerializer, MembergetSerializer,
    CentreclassesSerializer, CentreGetSerializer, CentrePOSTSerializer,
    Staffserializer, Staff_by_centre, FacilitiesSerializer,
    Facility_claases, create_facility,Classesgetserializer,Signup_serializer,Loginserializer
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.core.cache import cache
from .models import Centre
from rest_framework.permissions import AllowAny
from .decorators import member_required
import requests
from django.contrib.auth.models import User
from django.http import JsonResponse 
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Signup, Login  # ← both models 
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication 
import random   
from .utils import generate_otp
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings 
from .tasks import send_welcome_email

def send_otp_email(email, otp):
    message = Mail(
        from_email=settings.EMAIL_FROM,
        to_emails=email,
        subject="Your OTP Code",
        html_content=f"<strong>Your OTP is: {otp}</strong>"
    )
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    sg.send(message) 

@api_view(['POST'])
def verifyOTP(request, id):
    otp = request.data.get('otp')
    
    # ✅ Yeh line add karo
    try:
        otp = int(otp)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid OTP format"}, status=400)
    
    users_id = id
    if OTP.objects.filter(otp=otp, is_used=False, user_id=users_id).exists():
        otp_obj = OTP.objects.get(otp=otp, is_used=False)
        otp_obj.is_used = True
        otp_obj.save()
        related_obj = Signup.objects.get(id=users_id)
        related_obj.is_verified = True
        related_obj.save()
        return JsonResponse({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(['POST'])
def Signup_fun(request):
    ser = Signup_serializer(data=request.data)
    email = request.data.get('email') 


    print("REQUEST DATA:", request.data)


    if ser.is_valid():
        ser.save()

        otp = generate_otp() 
        print(f"Generated OTP: {otp}") 

        OTP.objects.create(user=ser.instance, otp=otp)
        fetched_id = ser.instance.id
        send_otp_email(email, otp)
        send_welcome_email.delay(email)      
        return JsonResponse({"message": "Signup successful. Please verify your email.", "user_id": fetched_id}, status=status.HTTP_201_CREATED)

    return JsonResponse({"errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_with_hms_token(request):
    hms_token = request.data.get('hms_token')
    if not hms_token:
        return Response({"error": "HMS token required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        hms_response = requests.get(
            f"{HMS_URL}/api/user-info/",
            headers={"Authorization": f"Bearer {hms_token}"}
        )
    except requests.exceptions.RequestException:
        return Response({"error": "Cannot connect to HMS"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if hms_response.status_code != 200:
        return Response({"error": "Invalid HMS token"}, status=status.HTTP_401_UNAUTHORIZED)

    user_data = hms_response.json()
    username = user_data.get("username")
    if not username:
        return Response({"error": "HMS user missing username"}, status=status.HTTP_400_BAD_REQUEST)

    user, created = User.objects.get_or_create(username=username)
    refresh = RefreshToken.for_user(user)

    return Response({
        "fms_access": str(refresh.access_token),
        "fms_refresh": str(refresh),
        "created": created
    })



@authentication_classes([JWTAuthentication])
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    serializer = Loginserializer(data=request.data)

    signup_obj=Signup.objects.filter(username=username).first() 
    if signup_obj.is_verified==False:
        return JsonResponse({"error":"Please verify your email first"},status=status.HTTP_401_UNAUTHORIZED) 


    else:
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)


        return Response(
         serializer.errors,
         status=status.HTTP_400_BAD_REQUEST
    )




@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@permission_classes([JWTAuthentication])


def Allcentres(request, id=None):

    if request.method == 'GET':

        if id is not None:
            try:
                cache_key = f'centre_{id}'        
                data = cache.get(cache_key)        

                if data is None:
                    print("MySQL se aa raha hai")
                    c = Centre.objects.get(id=id)
                    ser = CentreGetSerializer(c)
                    data = ser.data               
                    cache.set(cache_key, data, timeout=300)  
                    return JsonResponse(ser.data,many=True,safe=False,status=status.HTTP_200_OK)
                else:
                    print("Redis se aa raha hai ✅")

                return JsonResponse(data, status=status.HTTP_200_OK, safe=False)

            except Centre.DoesNotExist:
                return JsonResponse({"error": "Centre not exists"}, status=status.HTTP_404_NOT_FOUND)

        else:
            cache_key = 'all_centres'
            data = cache.get(cache_key)           

            if data is None:
                print("MySQL se aa raha hai")
                c = Centre.objects.all()
                ser = CentreGetSerializer(c, many=True)
                data = ser.data                 
                cache.set(cache_key, data, timeout=300)
            else:
                print("Redis se aa raha hai ")

            return JsonResponse(list(data), status=status.HTTP_200_OK, safe=False)

    elif request.method == 'POST':
        ser = CentrePOSTSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return JsonResponse(ser.data, safe=False, status=status.HTTP_201_CREATED)
        return JsonResponse(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        c = Centre.objects.get(id=id)
        ser = CentrePOSTSerializer(c,data=request.data,partial=True)
        if ser.is_valid():
            ser.save()
            return JsonResponse(ser.data, safe=False, status=status.HTTP_201_CREATED)
        return JsonResponse(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        c = Centre.objects.get(id=id)
        ser = CentrePOSTSerializer(c,data=request.data,partial=True)
        if ser.is_valid():
            ser.save()
            return JsonResponse(ser.data, safe=False, status=status.HTTP_201_CREATED)
        return JsonResponse(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            c = Centre.objects.get(id=id)
            c.delete()
        except Centre.DoesNotExist:
            return JsonResponse({"error": "centre does not exist"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def show_members(request):

    cache_key='members'
    data=cache.get(cache_key) 

    if data is None:
      m = Member.objects.all()
      ser = MembergetSerializer(m, many=True)
      cache.set(cache_key, data, timeout=300)
      return JsonResponse(ser.data,safe=False, status=status.HTTP_202_ACCEPTED) 
    else :
        print("redis se ara") 

        return JsonResponse(data,status=status.HTTP_200_OK)


@api_view(['GET'])
def show_centre(request, id=None):
    if id is not None:
        c = Centre.objects.get(id=id)
        ser = Centre_user_serializer(c)
        return JsonResponse(ser.data, status=status.HTTP_200_OK)
    else:

        cache_key='centre_BY_id'
        data=cache.get(cache_key) 
        if data is None:   
         print("mysql se ara")
         c = Centre.objects.all()
         ser = Centre_user_serializer(c, many=True)
         data=ser.data
         cache.set(cache_key,data,timeout=300)
         print("mysql se ara")
         return JsonResponse(ser.data,safe=False, status=status.HTTP_200_OK) 
        
        else:
            print("redis se ara") 
            return JsonResponse(data,safe=False,status=status.HTTP_200_OK)


@api_view(['GET'])
@member_required
def Centre_classes(request, id=None):
    c = Centre.objects.prefetch_related('Facilities').get(id=id)
    ser = CentreuserSerializer(c)
    return JsonResponse(ser.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_centre_classes(request, id=None):
    c = Centre.objects.prefetch_related('class_set').get(id=id)
    ser = CentreclassesSerializer(c)
    return JsonResponse(ser.data, safe=False, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT', 'PATCH'])
def staff_data(request, id=None):
    if request.method == 'GET' and id is not None:
        s = Staff.objects.get(id=id)
        ser = Staffserializer(s)
        return JsonResponse(ser.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        ser = Staffserializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return JsonResponse({"Created": "Staff created successfully"}, ser.data, status=status.HTTP_201_CREATED)
        return JsonResponse(ser.errors, status=status.HTTP_308_PERMANENT_REDIRECT)

    elif request.method == 'PATCH':
        s = Staff.objects.get(id=id)
        ser = Staffserializer(s, data=request.data)
        if ser.is_valid():
            ser.save()
        return JsonResponse(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        s = Staff.objects.get(id=id)
        ser = Staffserializer(s, data=request.data)
        if ser.is_valid():
            ser.save()
        return JsonResponse(ser.errors, status=status.HTTP_400_BAD_REQUEST)


def get_facilities(request, id=None):
    if request.method == 'GET' and id is None:
        f = Facilities.objects.all()
        ser = FacilitiesSerializer(f, many=True)
        return JsonResponse(ser.data, status=status.HTTP_200_OK)

    elif request.method == 'GET' and id is not None:
        f = Facilities.objects.get(id=id)
        ser = FacilitiesSerializer(f, many=True)
        return JsonResponse(ser.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_staff_by_centre(request, id=None):
    s = Staff.objects.filter(Centre_id_id=id)
    ser = Staffserializer(s, many=True)
    return JsonResponse(ser.data, safe=False, status=status.HTTP_200_OK)


def get_staff_by_role(request):
    role_come= request.GET.get('role')
    staff = Staff.objects.filter(Staff_Role=role_come)
    
        
    ser = Staffserializer(staff, many=True)
    return JsonResponse(ser.data,safe=False, status=status.HTTP_200_OK)


def staff_detail(request, id=None):
    if request.method == 'GET' and id is None:
        staff = Staff.objects.all()
        ser = Staffserializer(staff, many=True) 
        return JsonResponse(ser.data,safe=False,status=status.HTTP_200_OK)
    elif request.method == 'GET' and id is not None:
        s = Staff.objects.get(id=id)
        ser = Staffserializer(s)
        return JsonResponse(ser.data, status=status.HTTP_200_OK)
    elif request.method == 'PATCH':
        s = Staff.objects.get(id=id)
        ser = Staffserializer(s, data=request.data)
        if ser.is_valid():
            ser.save()
        return JsonResponse(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PUT':
        s = Staff.objects.get(id=id)
        ser = Staffserializer(s, data=request.data)
        if ser.is_valid():
            ser.save()
            return JsonResponse(ser.data, status=status.HTTP_202_ACCEPTED)
        return JsonResponse(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        s = Staff.objects.get(id=id)
        s.delete()
        return JsonResponse({'Deleted': 'Staff is deleted successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_staff(request):
    s = Staffserializer(data=request.data)
    if s.is_valid():
        s.save()
        return JsonResponse(s.data, status=status.HTTP_201_CREATED)
    return JsonResponse(s.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE', 'PATCH', 'PUT'])
def get_all_facilities(request, id=None):
    if request.method == 'GET':
        f = Facilities.objects.all()
        ser = FacilitiesSerializer(f, many=True)
        return JsonResponse(ser.data, safe=False, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        ser = FacilitiesSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return JsonResponse(ser.data, status=status.HTTP_201_CREATED)
        return JsonResponse(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:

            
            f = Facilities.objects.get(pk=id)
            f.delete()
            return JsonResponse({"message": "Deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Facilities.DoesNotExist:
            return JsonResponse({"error": "Facility not found"}, status=404)
    elif request.method in ['PATCH', 'PUT']:
        try:
            f = Facilities.objects.get(pk=id)
        except Facilities.DoesNotExist:
            return JsonResponse({"error": "Facility not found"}, status=404)
        ser = FacilitiesSerializer(f, data=request.data, partial=(request.method == 'PATCH'))
        if ser.is_valid():
            ser.save()
            return JsonResponse(ser.data, status=status.HTTP_200_OK)
        return JsonResponse(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_classes_by_facility(request, id=None):
    try:
        facility = Facilities.objects.prefetch_related('Classes').get(pk=id)
    except Facilities.DoesNotExist:
        return JsonResponse({"error": f"Facility with id={id} not found"}, status=404)
    ser = Facility_claases(facility)  # single object → no many=True
    return JsonResponse(ser.data, safe=False, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_facility(request):
    ser = FacilitiesSerializer(data=request.data) 
    if ser.is_valid():
        ser.save()
        return JsonResponse(ser.data, safe=False, status=status.HTTP_201_CREATED)
    return JsonResponse(ser.errors, safe=False, status=status.HTTP_400_BAD_REQUEST)








## Classes Api's 


@api_view(['GET','POST','PUT','PATCH']) 

def get_classes(request,id=None):

    if request.method=='GET' and id is None: 
      obj=Class.objects.all() 
      ser=Classesgetserializer(obj,many=True) 
      return JsonResponse(ser.data,safe=False,status=status.HTTP_200_OK) 
    
    elif request.method=='GET' and id is not None: 
        obj=Class.objects.filter(Class_no=id) 
        ser=Classesgetserializer(obj,many=True) 
        return JsonResponse(ser.data,safe=False,status=status.HTTP_200_OK)  
    

    
@api_view(['POST'])
def create_class(request):  

    ser=Classesgetserializer(data=request.data) 

    if ser.is_valid(): 
        ser.save() 
        return JsonResponse(ser.data,status=status.HTTP_201_CREATED) 
    return JsonResponse(ser.errors,status=status.HTTP_400_BAD_REQUEST) 


    






    
    


