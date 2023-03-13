from django.shortcuts import render,redirect
from carts.models import CartItem
from django.contrib import messages
from django.http import HttpResponse

from orders.forms import OrderForm
from orders.models import Order,Payment
# Create your views here.
import datetime
import json

def place_order(request,total = 0,quantity = 0):
    
    
    current_user = request.user
    
    # if carts count <= 0 redirect to store
    cart_items = CartItem.objects.filter(user = current_user)
    count = cart_items.count()
    if count <= 0:
        return redirect('store')
    

    # # same as carts.views.cart
    tax = 0
    grand_total = 0

    for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    tax = (2*total)/100
    grand_total = tax + total
    
    if request.method == "POST":
        form = OrderForm(request.POST)

        data = Order()

        data.user = current_user
        if form.is_valid():

            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax= tax
            data.ip = request.META.get("REMOTE_ADDR")
            data.save()

            # generate order number

            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime("%m"))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210310

            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user = current_user,is_ordered = False,order_number = order_number)
            # after payment we have to true is_ordered
            context = {
                 "order":order,
                 "cart_items":cart_items,
                 "total":total,
                 "tax":tax,
                 "grand_total":grand_total
            }
            return render(request,"orders/payments.html",context=context)
        else:
            # this is run if in html name is diff from form and form in try except block
            messages.error(request,"form is not submitted try again")
             
    else:
         return redirect("checkout")


def payments(request):
    body = json.loads(request.body)
    print(body)
    # {'transID': '8WE0473310140123T', 'orderID': '2023031321', 'payment_method': 'Paypal',\
    #  'status': 'COMPLETED'}
    order = Order.objects.get(user = request.user,is_ordered = False,order_number = body.get("orderID"))

    payment = Payment(
         user = request.user,
         payment_id = body.get("transID"),
         payment_method = body.get("payment_method"),
         amount_paid = order.order_total,
         status = body.get("status"),
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()


    # store transactions inside the modal
    return render(request,"orders/payments.html")