from rest_framework import serializers
from courses.models import Course,Module,Content,Enrollment,Progress,RazorpayOrder
from django.db.models import Case, When, Value, IntegerField


class CourseSerializer(serializers.ModelSerializer):
    course_modules = serializers.SerializerMethodField()
    class Meta(object):
        model = Course
        fields = ['id','title','description','image','category','price','creator','keyword','review','created_at','updated_at','course_modules']
        
    def get_course_modules(self,obj):
        modules = Module.objects.filter(course=obj.id)
        return len(modules)


class ModuleSerializer(serializers.ModelSerializer):
    content_desc = serializers.SerializerMethodField()
    class Meta(object):
        model = Module
        fields = ['id','title','description','order','course','created_at','content_desc','updated_at']
    
    def get_content_desc(self, obj):
        content = Content.objects.filter(module=obj.id).annotate(
            content_order=Case(
                When(content_type='video', then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            )
        ).order_by('content_order', 'content_type')
        serializer = ContentSerializer(content, many=True)
        return serializer.data


class ContentSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Content
        fields = ['id','content_type','title','data','module','image_video','created_at','updated_at']
        

class RazorPayOrderSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = RazorpayOrder
        fields = ['id','course','student','total_amount','amount_paid','currency','order_id']


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Enrollment
        fields = ['id','student','course','transaction_type','total_amount','amount_paid','transaction_time','razorpay','completed']
        

class EnrollmentListSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField() 
    course_description = serializers.SerializerMethodField()
    class Meta(object):
        model = Enrollment
        fields = ['id','student','course','total_amount','course_name','course_description']
    
    def get_course_name(self,obj):
        return obj.course.title
    def get_course_description(self,obj):
        return obj.course.description

class ProgressSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Progress
        fields = ['id','user','course','module','content','completed_at']