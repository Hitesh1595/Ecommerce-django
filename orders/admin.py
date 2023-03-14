from django.contrib import admin

from orders.models import Payment,Order,OrderProduct

# Register your models here.

# make table in Order

admin.register(OrderProduct)
class OrderProductInLine(admin.TabularInline):
    model = OrderProduct
    # by defaut django give 3 row in table so we have to pass 0
    extra = 0

    readonly_fields = ["payment","user","product","quantity","product_price","ordered"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number","full_name","phone","email","city","order_total","tax","status",\
                    "is_ordered","created_at"]
    list_filter = ["status","is_ordered"]

    search_fields = ["order_number","first_name","last_name","phone","email"]

    list_per_page = 20
    

    inlines = [OrderProductInLine]

admin.site.register([Payment])
