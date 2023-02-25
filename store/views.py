from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse

# Create your views here.
from store.models import Product
from category.models import Category

from carts.models import CartItem
# check if item is present or not in CartItem
from carts.views import _cart_id

from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator

def store(request, category_slug = None):
     # if sub category is there like shirts/shoes/etc...
    if category_slug:
        categories = get_object_or_404(Category,slug = category_slug)
        products = Product.objects.all().filter(category = categories,is_available  = True).order_by('id')

        paginator = Paginator(products,2)
        # to know the page no from url like that url/?page = 2
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    else:
        products = Product.objects.all().filter(is_available  = True).order_by('id')
        # pass only 6 items in one page from all products
        paginator = Paginator(products,6)
        # to know the page no from url like that url/?page = 2
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        
    product_count = products.count()

    context = {
        "products":paged_products,
        "product_count":product_count
    }
    return render(request,'store/store.html',context=context)



def product_detail(request,category_slug = None,product_slug = None):

    try:
        # category__slug means category in product and __slug came from category that is foriegn key to product
        # slug = product_slug is came from product slug
        single_product = Product.objects.get(category__slug = category_slug,slug = product_slug)
        # cart__cart_id = cart present in CartItem
        # __cart_id(cart_id) is foreign key in that so directly call id(card_id)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request)).exists()
    except Exception as e:
        raise e

    context = {
        "single_product" : single_product,
        "in_cart":in_cart
    }
    return render(request,'store/product_detail.html',context=context)


def search(request):
    return HttpResponse("serach")