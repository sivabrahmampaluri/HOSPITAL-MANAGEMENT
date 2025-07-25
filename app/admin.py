from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FileUpload

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

admin.site.register(User, CustomUserAdmin)

class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('file', 'user', 'uploaded_at')

admin.site.register(FileUpload, FileUploadAdmin)
