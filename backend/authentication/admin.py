from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import AdminUser, UniversityProfile


@admin.register(AdminUser)
class AdminUserAdmin(BaseUserAdmin):
    """Admin configuration for AdminUser model."""
    
    list_display = [
        'username', 'email', 'role', 'first_name', 'last_name', 
        'is_active', 'is_staff', 'date_joined'
    ]
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'student_id', 'employee_id']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Role & IDs', {
            'fields': ('role', 'student_id', 'employee_id', 'department')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Security', {
            'fields': ('two_factor_enabled', 'two_factor_secret')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'role', 'first_name', 'last_name'
            ),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


@admin.register(UniversityProfile)
class UniversityProfileAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'tagline',
        'contact_email',
        'contact_phone',
        'updated_at',
    )
    search_fields = ('name', 'tagline', 'contact_email', 'contact_phone')
