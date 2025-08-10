from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ContactInfo

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username',)
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'username')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

# Admin configuration for the ContactInfo model
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address', 'city', 'district', 'state', 'zipcode', 'added_on')
    list_filter = ('state', 'city', 'user')  # Filter options for state, city, and user
    search_fields = ('phone_number', 'address', 'city', 'state', 'user__email')  # Search by phone, address, city, state, or user email
    ordering = ('user',)  # Order by user

# Register the models with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ContactInfo, ContactInfoAdmin)
