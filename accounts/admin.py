from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm, CustomUserCreateForm
from .models import CustomUser

# Register your models here.

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreateForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'first_name', 'last_name', 'email', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('age', )}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('age',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)