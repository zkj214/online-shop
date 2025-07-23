from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.urls import reverse

from accounts.decorators import authorized_user
from accounts.forms import CreateUserForm, ImageUploadForm, RegisterCustomerForm
from django.contrib.auth.models import Group
from store.models import Customer, Order, CartItem
from django.contrib.auth import get_user_model
from accounts.forms import CustomerForm
from django.conf import settings
import os
# Create your views here.


User=get_user_model()
def login_user(request):
    year = date.today().year
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("store:admin_dashboard")

        return redirect("store:items")
    else:
        if request.method=="POST":
            email=request.POST.get("email")
            password = request.POST.get("password")

            user = authenticate(username=email,password=password)
            if user is not None:
                login(request,user)
                customer=Customer.objects.get(user=user)
                name=customer.name.split()[0]
                messages.success(request,f"You have been successfully logged in, {name}!")
                if request.user.is_staff:
                    return redirect("store:admin_dashboard")
                else:
                    return redirect("store:items")
            else:
                messages.error(request,"Oops, wrong username or password.")
                return redirect("accounts:login")

    context={"year":year}
    return render(request,"accounts/login.html",context)

def register_user(request):
    year = date.today().year
    if request.user.is_authenticated:
        return redirect("store:items")
    else:
        form=CreateUserForm()
        form2=CustomerForm()

        if request.method=="POST":
            form=CreateUserForm(request.POST)
            form2 = RegisterCustomerForm(request.POST)

            if form.is_valid and form2.is_valid:
                try:
                    user=form.save() # "user" referring to the form's model
                    customer=form2.save(commit=False) # the return object is the model of the form. Since it's custom-made
                                                  # model, the commit should be false.
                except ValueError:
                    messages.error(request, "Error encountered. Please try again.")
                    return redirect("accounts:register")

                customer.user=user #so that there would be a 1-to-1 relationship bet. user & customer
                customer.email=user.email

                if user.pk>1:
                    group,created=Group.objects.get_or_create(name="customer")
                    user.groups.add(group)
                else:
                    Group.objects.create(name="admin") # don't return a value when dealing with creating objects
                    group=Group.objects.get(name="admin")
                    user.groups.add(group)

                user.save()
                customer.save()
                messages.success(request,"Congrats! Your account has been created. You can now login.")
                return redirect("accounts:login")

    context = {"year": year,"form":form,"form2":form2}
    return render(request,"accounts/register.html",context)


def logout_user(request):
    logout(request)
    messages.success(request,"You have been logged out. Thanks for visiting.")
    return redirect("accounts:login")

def login_redirect(request):
    messages.info(request,"You must first login.")
    return redirect("accounts:login")


@login_required
def user_settings(request):
    year = date.today().year

    customer=Customer.objects.get(user=request.user)
    form=CustomerForm(instance=customer)
    form2 = ImageUploadForm(instance=customer)

    if request.method=="POST":
        form=CustomerForm(request.POST,instance=customer)
        if form.is_valid:
            form.save() #no operation being made that's why no "commit=False" and returned object
            messages.success(request,"Your information has been successfully updated.")
            if request.user.is_staff:
                return redirect("store:admin_dashboard")
            else:
                return redirect("store:dashboard")


    if not request.user.is_staff:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, status="Open")
        items = order.cartitem_set.all()  # 1-to-many relationship between order and cartitem models
        cartitems = order.get_cart_items
    else:
        items = []
        order = {
            "get_cart_total": 0,
            "get_cart_items": 0,
            "shipping": False
        }
        cartitems = order["get_cart_items"]

    context = {"items": items, "order": order, "cartitems": cartitems, "year": year,"form":form,"form2":form2}
    return render(request,"accounts/user_settings.html",context)


@login_required
@authorized_user(allowed_roles=["customer"])
def delete_account(request,pk):
    year = date.today().year
    if request.method=="POST":
        user=User.objects.get(pk=pk)
        customer=Customer.objects.get(user=user)
        order=Order.objects.get(customer=customer)
        cartitem,created=CartItem.objects.get_or_create(order=order)


        order.delete()
        user.delete()
        cartitem.delete()

        img_file=str(customer.profile_pic) # must be string type
        file_path=os.path.join(settings.MEDIA_ROOT,img_file)

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except PermissionError:
            pass

        customer.delete()
        logout(request) # must log out
        messages.info(request,"Your account has been deleted.")
        return redirect("store:index")

    if not request.user.is_staff:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, status="Open")
        items = order.cartitem_set.all()  # 1-to-many relationship between order and cartitem models
        cartitems = order.get_cart_items
    else:
        items = []
        order = {
            "get_cart_total": 0,
            "get_cart_items": 0,
            "shipping": False
        }
        cartitems = order["get_cart_items"]

    context = {"items": items, "order": order, "cartitems": cartitems, "year": year}
    return render(request,"accounts/account_confirm_delete.html",context)


@login_required
def upload_photo(request):
    customer=Customer.objects.get(user=request.user)

    if request.method=="POST":
        form=ImageUploadForm(request.POST,request.FILES,instance=customer)
        if form.is_valid:
            try:
                customer.profile_pic.delete()
                customer=form.save(commit=False)
            except ValueError:
                messages.error(request, "Sorry, unaccepted file type. Please try again.")
                return redirect("accounts:settings")

            if "profile_pic" in request.FILES:
                customer.profile_pic=request.FILES["profile_pic"]

            customer.save()
            messages.success(request,"Your photo has been successfully updated.")

            if request.user.is_staff:
                return redirect("store:admin_dashboard")
            else:
                return redirect("store:dashboard")