
from rest_framework import serializers
from .models import User ,User_role
from rest_framework import status
from .models import Centre, Facilities, Staff, Member, Enrollment, Class, Fitness_Asessment


class FacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facilities
        fields = '__all__'

class Staffserializer(serializers.ModelSerializer): 
    
    class Meta: 
        model=Staff
        fields= '__all__'


class Classesgetserializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'



class Memberserializer(serializers.ModelSerializer):
    
    class Meta: 
        model=Member 
        fields='__all__' 

class CentreGetSerializer(serializers.ModelSerializer):
    facilities = FacilitiesSerializer(source='Facilities', many=True) 
    staff=Staffserializer(source='staff_set',many=True) 
    member=Memberserializer(source='member_set',many=True)

    class Meta:
        model = Centre
        fields = ["Centre_name", "Centre_address",  "Centre_address", "phone_no","facilities","staff","member"]




class CentreuserSerializer(serializers.ModelSerializer): 
    facilities = FacilitiesSerializer(source='Facilities', many=True) 

    class Meta:
        model = Centre
        fields = ["Centre_name", "Centre_address",  "Centre_address", "phone_no","facilities"] 


class CentreclassesSerializer(serializers.ModelSerializer): 
         classes=Classesgetserializer(source='Class',many=True)

         class Meta:
           model = Centre
           fields = ["Centre_name", "Centre_address",  "Centre_address", "phone_no","classes"] 



class CentrePOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Centre
        fields = '__all__'

    def create(self, validated_data):
        manager = validated_data.get('Manager_id')

        if manager:
            # Check 1: Manager must have M role
            if manager.Staff_Role != 'M':
                raise serializers.ValidationError(
                    {'Manager_id': 'This staff is not a manager'}
                )

            # Check 2: Manager not already managing another centre
            try:
                if manager.managed_centre:
                    raise serializers.ValidationError(
                        {'Manager_id': 'This manager is already managing another centre'}
                    )
            except:
                pass

        centre = Centre.objects.create(**validated_data)
        return centre
 

class Centre_user_serializer(serializers.ModelSerializer):

    class Meta:
        model=Centre 
        fields='__all__'  



class MembergetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'


class Fitness_asessmentgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fitness_Asessment
        fields = '__all__'


class StaffgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'


class Classesgetserializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'


class Enrollmentsgetserializers(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'


class FacilitiesgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facilities
        fields = '__all__'




class SignupSerializer(serializers.ModelSerializer):
    
    
    role = serializers.ChoiceField(choices=User_role.ROLE_CHOICES, write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "role"]


    def create(self, validated_data):
       
         role = validated_data.pop("role")

        
         user = User.objects.create_user(**validated_data)

     
         User_role.objects.create(user=user, role=role)

         return user