from django.contrib import admin

# Register your models here.
from category.models import Category

# only to used to show in admin panel does not need any migrations
# admin.site.register(Category)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields =  {"slug" : ("category_name",)}
    list_display        =  ["category_name","slug"]
