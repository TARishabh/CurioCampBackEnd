from rest_framework import serializers
from user.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    
    class Meta(object):
        model = User
        fields = ['first_name','last_name','email','login_otp','date_of_birth','gender','phone_number','password','password2']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def validate_phone_number(self, value):
        if value:
            pattern = re.compile("^[6-9]\d{9}$")
            if not pattern.match(value):
                raise serializers.ValidationError("Phone Number Not accepted")
        return value

    def create(self, validated_data):
        user = User.objects.create(
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data['email'],
            profile = validated_data.get('profile', None),
            date_of_birth=validated_data.get('date_of_birth', None),
            gender=validated_data.get('gender', None),
            city = validated_data.get('city',''),
            country = validated_data.get('country',''),
            phone_number=validated_data.get('phone_number', None),
            login_otp=validated_data.get('login_otp', None),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id','email',]

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    city = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'profile', 'email', 'date_of_birth', 'gender', 'city', 'country', 'phone_number', 'password', 'password2']

    def update(self, instance, validated_data):
        # Update each field only if present in validated data
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.city = validated_data.get('city', instance.city)
        instance.country = validated_data.get('country', instance.country)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)

        # Update password if provided and valid
        password = validated_data.get('password')
        password2 = validated_data.get('password2')
        if password and password2 and password == password2:
            instance.set_password(password)
        
        instance.save()
        return instance

class GetUserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id','first_name','last_name','profile','email','date_of_birth','gender','city','country','phone_number']