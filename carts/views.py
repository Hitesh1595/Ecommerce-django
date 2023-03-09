from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required

# Create your views here.
from store.models import Product,Variation
from carts.models import Cart,CartItem


# for check purpose
from django.http import HttpResponse

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request,product_id):
    # http://127.0.0.1:8000/cart/add_cart/1/?color=red&size=small
    # form is submit and button on add cart in product_detail

     # get the product unique key
    product = Product.objects.get(id = product_id)
    if request.user.is_authenticated:
        # user login
        product_variation = []
        # check the method
        if request.method == "POST":
            # color = request.POST.get('color')
            # size = request.POST.get('size')
            for item in request.POST:
                key = item
                value = request.POST[key]

                # print(key,value)
                try:
                    variation = Variation.objects.get(product = product,variation_category__iexact = key,variation_value__iexact = value)
                    product_variation.append(variation)

                except:
                    pass
        

        # if cart item exist then inc quantity else create new

        is_cart_item_exists = CartItem.objects.filter(product = product,user = request.user).exists()

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product = product,user = request.user)
            # existing variation --> datbase
            # current variations --> product_variation(list)
            # item_id --> database
            
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            print(ex_var_list)
            if product_variation in ex_var_list:
                # increase the quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]

                item = CartItem.objects.get(product = product,id = item_id)

                item.quantity += 1
                item.save()

            # add the product variation in cartitem variation field
            # clear is used to add seperated item with diff combination
            else:
                # create the new with diffent variations
                item = CartItem.objects.create(product = product,quantity = 1,user = request.user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)

                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = request.user
            )
        
            if len(product_variation) > 0:
                cart_item.variations.clear()
                
                cart_item.variations.add(*product_variation)
            cart_item.save()

        # for testing purpose only 
        # return HttpResponse(cart_item.quantity)
        
        return redirect('cart')
    else:
        product_variation = []
        # check the method
        if request.method == "POST":
            # color = request.POST.get('color')
            # size = request.POST.get('size')
            for item in request.POST:
                key = item
                value = request.POST[key]

                # print(key,value)
                try:
                    variation = Variation.objects.get(product = product,variation_category__iexact = key,variation_value__iexact = value)
                    product_variation.append(variation)

                except:
                    pass
        
    
        try:
            # get the cart using the _cart_id present in session(present in cookies in browser)
            cart = Cart.objects.get(cart_id = _cart_id(request))

        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        # if cart item exist then inc quantity else create new

        is_cart_item_exists = CartItem.objects.filter(product = product,cart = cart).exists()



        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product = product,cart = cart)
            # existing variation --> datbase
            # current variations --> product_variation(list)
            # item_id --> database
            
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            print(ex_var_list)
            if product_variation in ex_var_list:
                # increase the quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]

                item = CartItem.objects.get(product = product,id = item_id)

                item.quantity += 1
                item.save()

            # add the product variation in cartitem variation field
            # clear is used to add seperated item with diff combination
            else:
                # create the new with diffent variations
                item = CartItem.objects.create(product = product,quantity = 1,cart = cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)

                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart
            )
        
            if len(product_variation) > 0:
                cart_item.variations.clear()
                
                cart_item.variations.add(*product_variation)
            cart_item.save()

        # for testing purpose only 
        # return HttpResponse(cart_item.quantity)
        
        return redirect('cart')

def remove_cart(request,product_id,cart_item_id):
   
    product =  get_object_or_404(Product,id = product_id)
    
    
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product = product,user = request.user,id = cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product = product,cart = cart,id = cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
   
    product =  get_object_or_404(Product,id = product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product = product,user = request.user,id = cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product = product,cart = cart,id = cart_item_id)

    cart_item.delete()

    return redirect('cart')


def cart(request, total = 0,quantity = 0,cart_items = None):
    try:
        tax = 0
        grand_total = 0
        # cheeck if user is login then filter based upon user key else cart id
        if request.user.is_authenticated:
            cart_items = CartItem.objects.all().filter(user = request.user,is_active = True)
        else:
            cart =  Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart,is_active = True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = tax + total
    except:
        print("object not exist")
        pass
    
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    # print(total,quantity)

    return render(request,'store/cart.html',context=context)

@login_required(login_url = 'login')
def checkout(request, total = 0,quantity = 0,cart_items = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.all().filter(user = request.user,is_active = True)
        else:
            cart =  Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart,is_active = True)

      
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = tax + total
    except:
        print("object not exist")
        pass
    
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request,'store/checkout.html',context = context)