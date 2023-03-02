from django.shortcuts import render,redirect

# Create your views here.
from accounts.forms import RegistrationForm
from accounts.models import Account

# used inbuild messages
from django.contrib import messages,auth

from django.contrib.auth.decorators import login_required

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
            messages.success(request, "registration succesful")
            return redirect("register")
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
            # messages.success(request,"you are login now")
            return redirect("home")
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
