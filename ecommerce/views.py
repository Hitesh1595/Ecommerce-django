from django.shortcuts import render

from store import models




def home(request):
    # get all product with filter is_available
    products = models.Product.objects.all().filter(is_available  = True).order_by("created_date")

    # get the review of a specific product
    for product in products:
        reviews = models.ReviewRating.objects.filter(product_id = product.id,status = True)
    
    return render(request,'home.html',{"products":products})