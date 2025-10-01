from django.contrib import admin

# Register your models here.
from .models import UserCategory

@admin.register(UserCategory)
class UserCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
