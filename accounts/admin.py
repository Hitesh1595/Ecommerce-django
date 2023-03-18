from django.contrib import admin

# use this for password safety purpose 
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html


# Register your models here.
from accounts.models import Account,UserProfile

@admin.register(Account)
class AccountAdmin(UserAdmin):
    list_display = ('email','first_name','username','last_login','date_joined','is_active')

    # used to display link to click on admin
    list_display_links = ['email','first_name','username']
    readonly_fields = ['last_login','date_joined']
    ordering = ['-date_joined']

    filter_horizontal = ()
    list_filter = ()
    # used for password field
    fieldsets = ()

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src = "{}" width = "30" style = "border-radius:50%;">'.format(object.profile_picture.url))
    
    thumbnail.short_description = "Profile Picture"

    list_display = ["thumbnail","user","city","state"]

# admin.site.register(Account)