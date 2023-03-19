from django.contrib import admin
from store.models import Product,Variation,ReviewRating,ProductGallery

# pip install django-admin-thumbnails
# use to see photos in product gallary which is in products
import admin_thumbnails

# Register your models here.

# used to see the product photos in product objects

admin.register(ProductGallery)
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # shows the list for admin 
    list_display = ['product_name','price','stock','is_available','category','modified_date']
    # used for slug generation (T shirt ==> t-shit)
    prepopulated_fields = {"slug" : ("product_name",)}

    inlines = [ProductGalleryInline]

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


# admin.site.register([ProductGallery])