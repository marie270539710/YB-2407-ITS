from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, ParkingLog, AvailableSlot

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

@admin.register(ParkingLog)
class ParkingLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'slot', 'arrival_time', 'exit_time', 'autoexit')
    list_filter = ('user__username', 'slot')
    search_fields = ('user__username', 'slot')
    ordering = ('-arrival_time',)

    # Disable Add, Edit, Delete
    def has_add_permission(self, request):
        return False  # Prevent adding new logs manually

    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing logs

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deleting logs

@admin.register(AvailableSlot)
class AvailableSlotAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'slots')
    list_filter = ('timestamp', 'slots')
    search_fields = ('timestamp', 'slots')
    ordering = ('-timestamp',)

    # Disable Add, Edit, Delete
    def has_add_permission(self, request):
        return False  # Prevent adding new logs manually

    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing logs

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deleting logs