from django.db import models 
from django.contrib.auth.models import User 
from django.contrib.auth.hashers import make_password 
from django.contrib.auth.hashers import make_password, identify_hasher




class Signup(models.Model): 
   username=models.CharField(max_length=20,null=False) 
   email=models.EmailField() 
   password=models.CharField(max_length=500,null=False) 
   confirm_password=models.CharField(max_length=500,null=False)  
   is_verified = models.BooleanField(default=False, null=True)


   class Meta:
      db_table='Signup'
    

   def save(self,*args,**kwargs): 
    
     try:
        identify_hasher(self.password) 
     except ValueError:
        self.password = make_password(self.password)

     self.username=self.username.upper() 
     super().save(*args,**kwargs)



class OTP(models.Model):
    user = models.ForeignKey(Signup, on_delete=models.CASCADE, related_name="otps")
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)  # OTP use hone ke baad True

    def __str__(self):
        return f"{self.user.email} - {self.otp}"

    def is_expired(self):
        """
        OTP expiry check (5 minutes validity)
        """
        expiry_time = self.created_at + timedelta(minutes=5)
        return timezone.now() > expiry_time



class Login(models.Model): 
 
 username=models.CharField(max_length=30) 
 password=models.CharField(max_length=40) 


 class Meta: 
    db_table='Login'  






 


class User_role(models.Model):
   ROLE_CHOICES=(
      ('member','Member'),
      ('staff','Staff')
   )
   role=models.CharField(max_length=20,choices=ROLE_CHOICES)
   user=models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True) 
   

class Centre(models.Model):
   Centre_name=models.CharField(max_length=30)
   Centre_address=models.CharField(max_length=40)
   phone_no=models.IntegerField(unique=True) 
   Manager_id = models.OneToOneField(
        "Staff",
        on_delete=models.SET_NULL,
        null=True,  
        blank=True,  
        related_name='managed_centre'  
    ) 
   


   

class Staff(models.Model):
   ROLE_CHOICES = [
        ('A', 'Administration'),
        ('C', 'Cleaner'),
        ('D', 'Instructor Dry'),
        ('P', 'Instructor Pool'),
        ('M', 'Manager'),
        ('S', 'Sales'),
        ('T', 'Security'),
    ] 


   user=models.OneToOneField(User,on_delete=models.CASCADE) 
   First_name=models.CharField(max_length=20)
   Last_name=models.CharField(max_length=40)
   Phone_no=models.IntegerField(unique=True)
   joined_date=models.DateTimeField()
   Staff_Role=models.CharField(max_length=40,choices=ROLE_CHOICES)
   Centre_id=models.ForeignKey(Centre,on_delete=models.CASCADE)


class Facilities(models.Model):   
   facility_room_no=models.AutoField(primary_key=True)
   centre_id=models.ForeignKey(Centre,on_delete=models.CASCADE,related_name='Facilities')
   facility_name=models.CharField(max_length=20)
   Description=models.CharField(max_length=200)
   Capacity=models.IntegerField()







class Class(models.Model):
   Class_no=models.AutoField(primary_key=True) 
   Centre_id=models.ForeignKey(Centre,on_delete=models.CASCADE) 
   Facility_room_no=models.ForeignKey(Facilities,on_delete=models.CASCADE,related_name='Classes')
   Description=models.CharField(max_length=200)
   Start_date=models.DateField()
   Duration=models.IntegerField()
   Max_participant=models.IntegerField()
   No_of_sessions=models.IntegerField()
   Class_cost=models.FloatField()
   instruct_by=models.ManyToManyField(Staff) 
   

   

       



class Member(models.Model):
   user=models.OneToOneField(User,on_delete=models.CASCADE) 
   Name=models.CharField(max_length=20)
   Member_id=models.AutoField(primary_key=True) 
   Home_Centre_id=models.ForeignKey(Centre,on_delete=models.CASCADE)
   Address=models.CharField(max_length=40)
   Joined_date=models.DateField()
   Phone_no=models.IntegerField(unique=True) 
   classes=models.ManyToManyField(Class,through='Enrollment')     

   referred_by = models.ForeignKey(
    "self",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="referrals"
)
   

class Enrollment(models.Model):
   class_no=models.ForeignKey(Class,on_delete=models.CASCADE)
   member_id=models.ForeignKey(Member,on_delete=models.CASCADE)
   payment_date=models.DateField()

      


   class Meta:
    unique_together=('class_no','member_id') 


class Fitness_Asessment(models.Model):
   member_id=models.ForeignKey(Member,on_delete=models.CASCADE) 
   staff_id=models.ForeignKey(Staff,on_delete=models.CASCADE) 
   Asessment_date=models.DateField() 
   vo2_max=models.FloatField()
   blood_pressure=models.FloatField()
   Weight=models.FloatField()
   BMI=models.FloatField()



