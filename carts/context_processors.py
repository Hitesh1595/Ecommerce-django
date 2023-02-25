from carts.models import Cart,CartItem

from carts.views import _cart_id

from django.http import HttpResponse


def counter(request):
    cart_count = 0
    # in admin in url then it will no send anything
    if 'admin' in request.path:
        return {}

    try:
        cart = Cart.objects.filter(cart_id = _cart_id(request))
        
        cart_items = CartItem.objects.all().filter(cart = cart[:1])

        for cart_item in cart_items:
            cart_count += cart_item.quantity

    except CartItem.DoesNotExist:
        cart_count = 0

    return dict(cart_count = cart_count)
