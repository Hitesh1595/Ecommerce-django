from django.shortcuts import render,redirect,get_object_or_404

# Create your views here.
from accounts.forms import RegistrationForm,UserForm,UserProfileForm
from accounts.models import Account,UserProfile

# used inbuild messages
from django.contrib import messages,auth

from django.contrib.auth.decorators import login_required

# email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart,CartItem
from carts.views import _cart_id

import requests


def register(request):
    # check the form method is POST then all process is going
    if request.method == "POST":
        # pass to registration from
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]
            user = Account.objects.create(first_name = first_name, last_name = last_name, username = username, email = email,password = password)
            user.phone_number = phone_number
            user.save()
            # messages.danger(request,"message")

            # USER ACTIVATE ... make link to send email

            current_site = get_current_site(request)
            mail_subject = "Please activate you account"
            message = render_to_string("accounts/account_verification_email.html", {
                # upper user
                "user":user,
                "domain":current_site,
                # encode the user primary key so no one detect maik id
                "uid":urlsafe_base64_encode(force_bytes(user.pk)),
                # used one library to generate and chehck the token ids
                "token":default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            #-----------------------------------------------------------------------


            # messages.success(request, "thank you for register with us we have send you a verification mail to your mail")
            return redirect("/accounts/login?command=verification&email="+email)
    else:
        form = RegistrationForm()
    context = {
        'form':form
    }
    return render(request,'accounts/register.html',context = context)

def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email = email,password = password)

        if user is not None:
            # before login first we check if anything in carts if exist then after login show in carts
            try:
              
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
             
                if is_cart_item_exists:
                    # get all item with is assigned to same id
                    cart_item = CartItem.objects.filter(cart = cart)
                    

                    # getting the product variations by cart id
                    product_variations = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variations.append(list(variation))

                    # get the cart item from the user to access product variations
                    cart_item = CartItem.objects.filter(user = user)
                    
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    # product_variations = [1,6,4,3]
                    # ex_var_list = [4,6,7,8]
                    for pr in product_variations:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]

                            item = CartItem.objects.get(id = item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart = cart)


                            # assign to same user that us login
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                print("except block")
                pass
            auth.login(request,user)
            messages.success(request,"you are login now")
            # used to fetch previous url
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout
                params = dict(x.split("=") for x in query.split("&"))
                # & is used in split because it in next parama after & value is there
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect("dashboard")
        else:
            messages.error(request,"Invalid login credentials")
            return redirect("login")
    return render(request,'accounts/login.html')

# decorator first check if user is login then it logout
@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,"you are logout now")
    return redirect("login")


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)

    # cover various error
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,"congrats your account is activated")
        return redirect('login')
    else:
        messages.error(request,"invalid activation link")
        return redirect("register")



@login_required(login_url='login')   
def dashboard(request):
    from orders.models import Order
    orders = Order.objects.order_by("-created_at").filter(user_id = request.user.id,is_ordered = True)
    orders_count = orders.count()
    user_profile = UserProfile.objects.get(user_id = request.user.id)
    context = {
        "orders_count":orders_count,
        "user_profile":user_profile
    }
    return render(request,'accounts/dashboard.html',context = context)


def forgotPassword(request):

    if request.method == "POST":
        email = request.POST["email"]

        # first we check email exist or not
        if Account.objects.filter(email= email).exists():
            # NOTE
            # iexact means case insensitive but exact is case sensitive
            user = Account.objects.get(email__exact = email)

            # reset password email link
            current_site = get_current_site(request)
            mail_subject = "Please reset your password"
            message = render_to_string("accounts/reset_password_email.html", {
                # upper user
                "user":user,
                "domain":current_site,
                # encode the user primary key so no one detect maik id
                "uid":urlsafe_base64_encode(force_bytes(user.pk)),
                # used one library to generate and chehck the token ids
                "token":default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            messages.success(request,"password of reset email has been sent to your email")
            return redirect('login')
        else:
            messages.error(request,"acooount does not exist")
            return redirect("forgotPassword")

    return render(request, 'accounts/forgotPassword.html')


def reset_password_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)

    # cover various error
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        request.session["sid"] = uid
        messages.success(request,"please reset your password")
        return redirect("resetPassword")
    else:
        messages.error(request,"this link is expire")
        return redirect("login")
    
def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk = uid)

            # NOTE
            # user have to set pass instead of save
            user.set_password(password)
            user.save()
            messages.success(request,"password succesful change")
            return redirect("login")
        else:
            messages.error(request,"password doest not match please try again")
            return redirect('resetPassword')
    return render(request, 'accounts/resetPassword.html')

@login_required(login_url='login') 
def my_orders(request):
    from orders.models import Order
    orders = Order.objects.filter(user = request.user, is_ordered = True).order_by("created_at")

    context = {
        "orders":orders,
    }
    return render(request,"accounts/my_orders.html",context = context)

@login_required(login_url='login') 
def edit_profile(request):
    # get the instance for userprofile form
    userprofile = get_object_or_404(UserProfile,user = request.user)

    if request.method == "POST":
        # try not to create new object every time therefore use instance updated the user same object
        user_form = UserForm(request.POST,instance=request.user)
        # NOTE
        # request.FILES id used because we are using file upload(type file) in html edit_profile
        profile_form = UserProfileForm(request.POST,request.FILES,instance = userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,"Your Profile has been updated")
            return redirect("edit_profile")
        
    else:
        # if not post
        # then use to see value in fields using instance that are already in database
        user_form = UserForm(instance = request.user)
        profile_form = UserProfileForm(instance = userprofile)
    
    context = {
        "user_form":user_form,
        "profile_form":profile_form,
        "userprofile":userprofile,
    }


    return render(request,"accounts/edit_profile.html",context = context)




@login_required(login_url='login') 
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact = request.user.username)

        if new_password == confirm_password:
            sucess = user.check_password(current_password)
            if sucess:
                user.set_password(new_password)
                user.save()

                # automatically log out
                # auth.logout()

                messages.success(request,"Your password Updated Sucessfully")
                return redirect("change_password")
            else:
                messages.error(request,"Please enter valid current password")
                return redirect("change_password")


        else:
            messages.error(request,"new_password and confirm_password is not same")
            return redirect("change_password")
            

    return render(request,"accounts/change_password.html")



@login_required(login_url='login') 
def order_detail(request,order_id):
    from orders.models import OrderProduct,Order
    order_detail = OrderProduct.objects.filter(order__order_number = order_id)
    order = Order.objects.get(order_number = order_id)
    subtotal = 0

    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        "order_detail":order_detail,
        "order":order,
        "subtotal":subtotal

    }
    return render(request,"accounts/order_detail.html",context = context)