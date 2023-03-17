from django.contrib import admin
from store.models import Product,Variation,ReviewRating

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # shows the list for admin 
    list_display = ['product_name','price','stock','is_available','category','modified_date']
    # used for slug generation (T shirt ==> t-shit)
    prepopulated_fields = {"slug" : ("product_name",)}

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ['product','variation_category','variation_value','is_active']
    # make directly change from list view
    list_editable = ["is_active"]
    
    # filter on the basis of this right side bar open
    list_filter = ['product','variation_category','variation_value']

@admin.register(ReviewRating)
class RatingReviewAdmin(admin.ModelAdmin):

    list_display = ["product","user","rating","created_at"]


# admin.site.register([ReviewRating])