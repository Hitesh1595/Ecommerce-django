from django.shortcuts import render

from store import models


def home(request):
    # get all product with filter is_available
    products = models.Product.objects.all().filter(is_available  = True)
    
    return render(request,'home.html',{"products":products})