from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display =('email','first_name','last_name','username','phone')
    search_fields = ('email','first_name','last_name')
    readonly_fields =('date_joined', 'last_login')
    ordering=('email',)
    fieldsets =(
        ('Authentication',{
            'fields':('email','password')
        }),
        ('Personal Information',{
            'fields':('first_name','last_name','phone')
        }),
        ('Verification / Activity',{
            'fields':('email_verified_at','phone_verified_at','last_activity_at')
        }),
        ('Permissions',{
            'fields':('is_active','is_staff','is_superuser','groups','user_permissions')
        }),
        ('Important dates',{
            'fields':('last_login','date_joined')
        })
    )
