from django.shortcuts import render,redirect
from carts.models import CartItem
from django.contrib import messages
from django.http import HttpResponse,JsonResponse

from orders.forms import OrderForm
from orders.models import Order,Payment,OrderProduct
from store.models import Product
# Create your views here.
import datetime
import json
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


def place_order(request,total = 0,quantity = 0):
    
    
    current_user = request.user
    
    # if carts count <= 0 redirect to store
    cart_items = CartItem.objects.filter(user = current_user)
    count = cart_items.count()
    if count <= 0:
        return redirect("home")
    

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
    order = Order.objects.get(user = request.user,is_ordered = False,order_number = body["orderID"])

    payment = Payment(
         user = request.user,
         payment_id = body["transID"],
         payment_method = body["payment_method"],
         amount_paid = order.order_total,
         status = body["status"],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()
    

    # move the cart items to order product table
    cart_items = CartItem.objects.filter(user = request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True

        # NOTE
        # we can not assign many to many field before save 
        # it give an error so after save we will assign
        orderproduct.save()

        # set the variations in each product

        cart_item = CartItem.objects.get(id = item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id = orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()
         


        #reduce the quantity of the sold product
        product = Product.objects.get(id = item.product_id)
        product.stock -= item.quantity
        product.save()



    # clear the cart after payment
    CartItem.objects.filter(user = request.user).delete()


    # send emmail to customer
    try:
        mail_subject = "Thank you for your Order!"
        message = render_to_string("orders/order_received_email.html", {
            # upper user
            "user":request.user,
            "order":order,
            
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject,message,to=[to_email])
        send_email.send()
    except:
        print("mail is not work")


    # send back order nummber and transation id back to sendData via JSON format
    data = {
         "order_number":order.order_number,
         "transID":payment.payment_id
    }

    return JsonResponse(data)


    # store transactions inside the modal
    return render(request,"orders/payments.html")

def order_complete(request):
    order_number = request.GET.get("order_number")
    transID = request.GET.get("transID")

    try:
        order = Order.objects.get(order_number = order_number,is_ordered = True)
        ordered_products = OrderProduct.objects.filter(order_id = order.id)

        payment = Payment.objects.get(payment_id = transID)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
            'order':order,
            'order_products':ordered_products,
            "order_number":order_number,
            "payment_id":payment.payment_id,
            "payment":payment,
            "subtotal":subtotal,
        }
        return render(request,"orders/order_complete.html",context=context)
    except(Order.DoesNotExist,Payment.DoesNotExist):
        return redirect("home")
    