from django.urls import path,include

from store import views

app_name = 'store'

urlpatterns = [
    path("",views.store,name = "store"),
    path("<slug:category_slug>/",views.store, name = 'product_by_category'),
    path("<slug:category_slug>/<slug:product_slug>/",views.product_detail,name = "product_detail"),
    # path("search/", views.search, name = 'search')
]