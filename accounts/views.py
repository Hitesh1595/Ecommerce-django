from django.shortcuts import render,redirect

# Create your views here.
from accounts.forms import RegistrationForm
from accounts.models import Account

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
            auth.login(request,user)
            messages.success(request,"you are login now")
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
    return render(request,'accounts/dashboard.html')


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