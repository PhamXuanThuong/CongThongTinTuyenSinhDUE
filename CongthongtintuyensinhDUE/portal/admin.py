from django.contrib import admin
from .models import Faculty, Department


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'faculty_type', 'color', 'order', 'is_active')
    search_fields = ('code', 'name', 'slogan')
    list_filter = ('faculty_type', 'is_active')
    ordering = ('order', 'id')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'short_name', 'phone', 'email', 'order', 'is_active')
    search_fields = ('code', 'name', 'short_name')
    list_filter = ('is_active',)
    ordering = ('order', 'id')

