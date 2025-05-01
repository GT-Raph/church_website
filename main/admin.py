from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect, render
from django.urls import path
from .models import Event, Sermon, ContactMessage, Branch, Member  # GalleryImage
from django import forms


class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'membership_code')
    actions = ['generate_branch_codes']

    def generate_branch_codes(self, request, queryset):
        """Generate branch codes for selected branches in the admin panel."""
        for i, branch in enumerate(queryset, start=1):
            if not branch.membership_code:  # Only generate if code doesn't exist
                prefix = branch.name[:3].upper()
                unique_number = str(i).zfill(4)
                branch.membership_code = f"{prefix}-{unique_number}"
                branch.save()

        self.message_user(request, "Branch codes generated successfully.")

    generate_branch_codes.short_description = "Generate Branch Codes for Selected Branches"


admin.site.register(Branch, BranchAdmin)


# Customize Member Admin if needed
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'membership_code')
    search_fields = ('name', 'membership_code')
    list_filter = ('branch',)

admin.site.register(Member, MemberAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_time_range', 'is_recurring_display', 'event_image')
    search_fields = ('title',)
    list_filter = ('date', 'end_date', 'is_recurring', 'recurring_weekday', 'recurring_week_position')

    @admin.display(description="Event Image")
    def event_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="border-radius: 5px;" />'.format(obj.image.url))
        return "No Image"

    @admin.display(description="Event Date & Time")
    def date_time_range(self, obj):
        start_date = obj.date.strftime("%Y-%m-%d") if obj.date else "Unknown"
        end_date = obj.end_date.strftime("%Y-%m-%d") if obj.end_date else None
        start_time = obj.start_time.strftime("%I:%M %p") if obj.start_time else "TBA"
        end_time = obj.end_time.strftime("%I:%M %p") if obj.end_time else None

        if end_date:
            return f"{start_date} {start_time} - {end_date} {end_time or ''}"
        return f"{start_date} {start_time} - {end_time or ''}"

    def is_recurring_display(self, obj):
        if obj.is_recurring:
            if obj.recurring_weekday is not None and obj.recurring_week_position:
                weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                return f"Yes ({obj.recurring_week_position.capitalize()} {weekday_names[obj.recurring_weekday]})"
            elif obj.recurring_day:
                return f"Yes (Day {obj.recurring_day})"
        return "No"

    is_recurring_display.short_description = "Recurring"


admin.site.register(Event, EventAdmin)

# Customize Sermon Admin
class SermonAdmin(admin.ModelAdmin):
    list_display = ('title', 'speaker', 'date')
    search_fields = ('title', 'speaker')
    list_filter = ('date',)

admin.site.register(Sermon, SermonAdmin)


# Customize Contact Messages Admin (Read-Only)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('created_at',)
    readonly_fields = ('name', 'email', 'message', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(ContactMessage, ContactMessageAdmin)


# Custom Admin Panel Header
admin.site.site_header = "CCC Apenkwa Admin Panel"
admin.site.site_title = "CCC Apenkwa Admin"
admin.site.index_title = "Admin Panel"
