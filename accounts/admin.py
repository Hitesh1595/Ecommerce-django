from django.contrib import admin

# use this for password safety purpose 
from django.contrib.auth.admin import UserAdmin


# Register your models here.
from accounts.models import Account

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

# admin.site.register(Account)