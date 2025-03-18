from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Inline for Profile – show with User in admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Extend default UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    # Show profile fields in User list display (optional)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_plate_number', 'get_selected_slot')
    list_select_related = ('profile',)

    def get_plate_number(self, instance):
        return instance.profile.plate_number
    get_plate_number.short_description = 'Plate Number'

    def get_selected_slot(self, instance):
        return instance.profile.selected_slot
    get_selected_slot.short_description = 'Selected Slot'

# Unregister and re-register User with extended admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register Profile separately (optional, not required if using inline)
# admin.site.register(Profile)
