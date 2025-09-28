from django.contrib import admin

# Register your models here.
from .models import FinanceRecord
admin.site.register(FinanceRecord)