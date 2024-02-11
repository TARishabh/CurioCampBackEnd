from django.contrib import admin
from courses.models import Course,Module,Content,Enrollment,Progress,RazorpayOrder
from django import forms
# Register your models here.
from django.contrib.admin.sites import AdminSite

class CourseAdmin(admin.ModelAdmin):
    # Define which fields are displayed in the admin panel
    list_display = ('id','title', 'creator', 'created_at')
    readonly_fields = ['review',]


    def get_queryset(self, request):
        # Apply custom queryset based on user's permissions
        if request.user.is_actual_superuser == True and request.user.user_type == 'Instructor':
            return Course.objects.all()
        elif request.user.user_type == 'Instructor':
            return Course.objects.filter(creator=request.user)
        return super().get_queryset(request)

    def has_change_permission(self, request, obj=None):
        # Check if user has permission to change the course
        if obj is not None and request.user.user_type == 'Instructor':
            return obj.creator == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Check if user has permission to delete the course
        if obj is not None and request.user.user_type == 'Instructor':
            return obj.creator == request.user
        return super().has_delete_permission(request, obj)

admin.site.register(Course, CourseAdmin)

class ModuleAdmin(admin.ModelAdmin):
    # Define which fields are displayed in the admin panel
    list_display = ('id','title', 'order', 'course')
    readonly_fields = ['created_at','updated_at']

    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'course' and request.user.user_type == 'Instructor':
            # Filter courses created by the current user
            kwargs['queryset'] = Course.objects.filter(creator=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def get_queryset(self, request):
        # Apply custom queryset based on user's permissions
        if request.user.is_actual_superuser == True and request.user.user_type == 'Instructor':
            return Module.objects.all()
        elif request.user.user_type == 'Instructor':
            # Filter courses created by the current user
            courses = Course.objects.filter(creator=request.user)
            # Get IDs of courses created by the current user
            course_ids = courses.values_list('id', flat=True)
            # Filter modules related to courses created by the current user
            queryset = Module.objects.filter(course__id__in=course_ids)
            return queryset
        return None

    def has_change_permission(self, request, obj=None):
        # Check if user has permission to change the course
        if obj is not None and request.user.user_type == 'Instructor':
            return obj.course.creator == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Check if user has permission to delete the course
        if obj is not None and request.user.user_type == 'Instructor':
            return obj.course.creator == request.user
        return super().has_delete_permission(request, obj)

admin.site.register(Module,ModuleAdmin)

class ContentAdmin(admin.ModelAdmin):
    # Define which fields are displayed in the admin panel
    list_display = ('id','title','content_type','module')
    readonly_fields = ['created_at','updated_at']

    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.is_actual_superuser == True:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'module' and request.user.user_type == 'Instructor':
            # Filter courses created by the current user
            # kwargs['queryset'] = Course.objects.filter(creator=request.user)
            courses = Course.objects.filter(creator=request.user)
            course_ids = courses.values_list('id', flat=True)
            kwargs['queryset'] = Module.objects.filter(course__id__in=course_ids)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def get_queryset(self, request):
        # Apply custom queryset based on user's permissions
        if request.user.is_actual_superuser == True and request.user.user_type == 'Instructor':
            return Content.objects.all()
        elif request.user.user_type == 'Instructor':
            # Filter courses created by the current user
            courses = Course.objects.filter(creator=request.user)
            # Get IDs of courses created by the current user
            course_ids = courses.values_list('id', flat=True)
            # Filter modules related to courses created by the current user
            module = Module.objects.filter(course__id__in=course_ids)
            module_ids = module.values_list('id', flat=True)
            queryset = Content.objects.filter(module__id__in=module_ids)
            return queryset
        return None

    def has_change_permission(self, request, obj=None):
        # Check if user has permission to change the course
        if obj is not None and request.user.user_type == 'Instructor':
            return obj.module.course.creator == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Check if user has permission to delete the course
        if obj is not None and request.user.user_type == 'Instructor':
            return obj.module.course.creator == request.user
        return super().has_delete_permission(request, obj)

admin.site.register(Content,ContentAdmin)

class RazorpayAdmin(admin.ModelAdmin):
    # Define which fields are displayed in the admin panel
    list_display = ('id','course','student','amount_paid')
    readonly_fields = ['student','course','amount_paid','total_amount','currency','order_id']

    def get_queryset(self, request):
        # Apply custom queryset based on user's permissions
        if request.user.is_actual_superuser == True and request.user.user_type == 'Instructor':
            return RazorpayOrder.objects.all()
        elif request.user.user_type == 'Instructor':
            return None
            # return queryset
        return None
    
    def has_change_permission(self, request, obj=None):
        return False
        # Check if user has permission to change the course
        # if obj is not None and request.user.user_type == 'Instructor':
            # return obj.module.course.creator == request.user
        # return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Check if user has permission to delete the course
        return False
        # if obj is not None and request.user.user_type == 'Instructor':
            # return obj.module.course.creator == request.user
        # return super().has_delete_permission(request, obj)

admin.site.register(RazorpayOrder,RazorpayAdmin)

class EnrollmentAdmin(admin.ModelAdmin):
    # Define which fields are displayed in the admin panel
    list_display = ('id','course','student','amount_paid')
    readonly_fields = ['student','course','amount_paid','total_amount','razorpay_id','transaction_type','completed']

    def get_queryset(self, request):
        # Apply custom queryset based on user's permissions
        if request.user.is_actual_superuser == True and request.user.user_type == 'Instructor':
            return Enrollment.objects.all()
        elif request.user.user_type == 'Instructor':
            return None
            # return queryset
        return None


admin.site.register(Enrollment,EnrollmentAdmin)
admin.site.register(Progress)
