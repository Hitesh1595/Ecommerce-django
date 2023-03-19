from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse
from django.db.models import Q

# Create your views here.
from store.models import Product,ReviewRating,ProductGallery
from category.models import Category
from orders.models import OrderProduct

from carts.models import CartItem
# check if item is present or not in CartItem
from carts.views import _cart_id
from store.forms import ReviewForm

from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.contrib import messages

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
    
    # NOTE
    # check whether user is purchased or not then it will review
    # this will written after review functionality added(review model created)
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user = request.user,product_id = single_product.id).exists()

        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # get the review of a specific product
    reviews = ReviewRating.objects.filter(product_id = single_product.id,status = True)

    # get the product Gallery
    product_gallery = ProductGallery.objects.filter(product_id = single_product.id)


    context = {
        "single_product" : single_product,
        "in_cart":in_cart,
        "orderproduct":orderproduct,
        "reviews":reviews,
        "product_gallery":product_gallery,
    }
    return render(request,'store/product_detail.html',context=context)


def search(request):
    # http://127.0.0.1:8000/store/search/?keyword=jhdjd
    # check keyword because we pass in navbar(submit form) in GET
    products = None
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            # filter(value,value) behave as AND operator
            # filter (Q(value) | Q(value)) behave as OR operator
            # from django.db.models import Q
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains = keyword)|Q(product_name__icontains = keyword))
            product_count = products.count()
            
    context = {
        'products':products,
        'product_count':product_count
    }
    return render(request,'store/store.html',context=context)


def submit_review(request,product_id):
    # use to store same url that we are using
    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        # user__id is foreign key in review rating modal same for product
        try:
            reviews = ReviewRating.objects.get(user__id = request.user.id,product__id = product_id)

            # NOTE
            # if you are using instance then it will check whether there is any review
            # if not  then bydefault it will create new review
            form = ReviewForm(request.POST,instance=reviews)
            form.save()
            messages.success(request,"thank you Your review has been updated")
            return redirect(url)


        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data["subject"]
                data.rating = form.cleaned_data["rating"]
                data.review = form.cleaned_data["review"]
                data.ip = request.META.get("REMOTE_ADDR")
                data.product_id = product_id
                data.user_id = request.user.id

                data.save()
                messages.success(request,"thank you Your review has been submitted")
                return redirect(url)

    