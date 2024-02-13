from django.db import models
from user.models import User
# Create your models here.


class Course(models.Model):
    review_choices = [
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(null=True,blank=True)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    keyword = models.CharField(null=True,blank=True,max_length=40)
    review = models.CharField(max_length=5,choices = review_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.id},{self.title}'
    


class Module(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'{self.id}, {self.title}'


class Content(models.Model):
    CONTENT_TYPES_CHOICES = (
        ("video", "Video"),
        ("text", "Text"),
        ("quiz", "Quiz"),
        # ... other content types
    )
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES_CHOICES)
    title = models.CharField(max_length=255)
    data = models.TextField(null=True,blank=True)
    image_video = models.FileField(null=True,blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}, {self.title}'


class RazorpayOrder(models.Model):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL,null=True,blank=True)
    student = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    total_amount = models.FloatField()
    amount_paid = models.FloatField()
    currency = models.CharField(max_length=10)
    order_id = models.CharField(max_length=20)


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    transaction_type = models.CharField(choices=(('cash','cash'),('card','card'),('online','online')), max_length=30,null=False,blank=False)
    total_amount = models.FloatField(null=False,blank=False)
    amount_paid = models.FloatField(null=False,blank=False)
    transaction_time = models.DateTimeField(auto_now_add=True)
    razorpay_id = models.ForeignKey(RazorpayOrder, on_delete=models.SET_NULL,null=True,blank=True,related_name="payment")
    completed = models.BooleanField(default=False)


class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="progress")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="progress", null=True, blank=True)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name="progress", null=True, blank=True)
    is_completed =  models.BooleanField(default=True)
    completed_at = models.DateTimeField(null=True, blank=True)