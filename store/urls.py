from django.urls import path,include

from store import views

app_name = 'store'

urlpatterns = [
    path("",views.store,name = "store"),
    path("category/<slug:category_slug>/",views.store, name = 'product_by_category'),
    path("category/<slug:category_slug>/<slug:product_slug>/",views.product_detail,name = "product_detail"),
    # http://127.0.0.1:8000/store/search/?keyword=jhdjd
    # came from navbar submit form
    path("search/", views.search, name = 'search'),

    path("submit_review/<int:product_id>/",views.submit_review,name = "submit_review"),
]