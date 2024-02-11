from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from user.manager import UserManager



class User(AbstractUser):

    user_type_choices = [
        ('Student','Student'),
        ('Instructor','Instructor'),
    ]
    gender_choices = [
        ('Male','Male'),
        ('Female','Female'),
        ('Other','Other'),
        ('PreferNotToSay','Prefer Not To Say')
    ]
    username = None
    first_name = models.CharField(max_length=20, blank=False,null=False)
    last_name = models.CharField( max_length=20, blank=False,null=False)
    email = models.EmailField(blank=False,null=False,unique=True)
    profile = models.ImageField(null=True,blank=True)
    date_of_birth = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=20, blank=True,null=True,choices=gender_choices)
    city = models.CharField(max_length=30,blank=True,null=True)
    country = models.CharField(max_length=30,blank=True,null=True)
    phone_number = models.CharField(max_length=20, unique=False)
    user_type = models.CharField(max_length=20,default='Student',null=True, blank=True)
    login_otp = models.CharField(max_length=6,null=True,blank=True)
    instructor_otp = models.CharField(max_length=6,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    is_actual_superuser = models.BooleanField(default=False)
    
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()
    

    def __str__(self) -> str:
        return f'{self.id},{self.email}'
