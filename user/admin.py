from django.contrib import admin
from user.models import User
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['id','email',]
    # list_filter = ['user_type']
    search_fields = ['email']
    
    def get_queryset(self, request):
        # Apply custom queryset based on user's permissions
        if request.user.is_actual_superuser == True and request.user.user_type == 'Instructor':
            return User.objects.all()
        elif request.user.user_type == 'Instructor':
            return None
            # return queryset
        return None
admin.site.register(User,UserAdmin)
