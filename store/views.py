from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from store.forms import ProductForm,ItemUpdateForm
from store.models import *
from django.http import JsonResponse
import json
from datetime import datetime,date
from decimal import Decimal   # convert to decimal type
from django.core.paginator import Paginator
from django.contrib import messages
from accounts.decorators import *
import os
from django.conf import settings
from django.db.models import Q
# Create your views here.


def search_item(request):
    year = date.today().year
    if request.method=="POST":
        if request.user.is_authenticated and not request.user.is_staff:
            customer, created = Customer.objects.get_or_create(user=request.user)
            order,created=Order.objects.get_or_create(customer=customer,status="Open")
            items = order.cartitem_set.all()  # 1-to-many relationship between order and cartitem models
            cartitems = order.get_cart_items
        else:
            items = []
            order = {
                "get_cart_total": 0,
                "get_cart_items": 0
            }
            cartitems = order["get_cart_items"]

        keyword=request.POST.get("keyword")
        products=Product.objects.filter(name__icontains=keyword)
        count=products.count()

        if keyword=="":
            messages.warning(request,"Oops, you forgot to enter an item to search. Pls try again...")
            return redirect("store:items")

        p = Paginator(products, 3)
        page = request.GET.get("page")
        products = p.get_page(page)
        nums = "a" * products.paginator.num_pages
        context = {"cartitems":cartitems,"keyword": keyword, "products": products, "count": count, "nums":nums,"year":year}
        return render(request, "store/search_item.html", context)

    context={"year":year}
    return render(request, "store/search_item.html",context)


def item_display(request):
    year=date.today().year

    if request.user.is_authenticated and not request.user.is_staff: # meaning user is authenticated but not admin
        customer,created=Customer.objects.get_or_create(user=request.user)
        order,created=Order.objects.get_or_create(customer=customer,status="Open")
        items=order.cartitem_set.all() # 1-to-many relationship between order and cartitem models
        cartitems=order.get_cart_items
    else:
        items=[]
        order={
            "get_cart_total":0,
            "get_cart_items":0
        }
        cartitems=order["get_cart_items"]


    products=Product.objects.all()
    p=Paginator(products,3)
    page=request.GET.get("page")
    products=p.get_page(page)
    nums="a"*products.paginator.num_pages
    count=len(products)

    context={"products":products,"nums":nums,"cartitems":cartitems,"year":year,"count":count}
    return render(request,"store/items_list.html",context)

@login_required
@authorized_user(allowed_roles=["customer"])
def cart(request):
    year = date.today().year
    if not request.user.is_staff: # meaning if the user is not admin
        customer,created=Customer.objects.get_or_create(user=request.user)
        order,created=Order.objects.get_or_create(customer=customer,status="Open")
        items=order.cartitem_set.all() # 1-to-many relationship between order and cartitem models
        cartitems=order.get_cart_items
    else:
        items=[]
        order={
            "get_cart_total":0,
            "get_cart_items":0
        }
        cartitems=order["get_cart_items"]

    context={"items":items,"order":order,"cartitems":cartitems,"year":year}
    return render(request,"store/cart.html",context)

@login_required
@authorized_user(allowed_roles=["customer"])
def checkout(request):
    year = date.today().year
    if not request.user.is_staff:
        customer,created=Customer.objects.get_or_create(user=request.user)
        order,created=Order.objects.get_or_create(customer=customer,status="Open")
        items=order.cartitem_set.all() # 1-to-many relationship between order and cartitem models
        cartitems = order.get_cart_items
    else:
        items=[]
        order={
            "get_cart_total":0,
            "get_cart_items":0,
            "shipping":False
        }
        cartitems = order["get_cart_items"]

    context={"items":items,"order":order,"cartitems":cartitems,"year":year}
    return render(request,"store/checkout.html",context)


@login_required
@authorized_user(allowed_roles=["customer"])
def UpdateCart(request):
    data=json.loads(request.body) # reads the json data
    productId=data["productId"]
    action=data["action"]
    print(f"Action:{action}")
    print(f"Product:{productId}")

    customer,created=Customer.objects.get_or_create(user=request.user)
    product=Product.objects.get(pk=productId)
    order,created=Order.objects.get_or_create(customer=customer,status="Open")
    cartitem,created=CartItem.objects.get_or_create(order=order,product=product)

    if action=="add":
        cartitem.quantity+=1
    elif action=="remove":
        cartitem.quantity-=1

    cartitem.save()

    if cartitem.quantity==0:
        cartitem.delete()

    return JsonResponse("Item was added.",safe=False)


@login_required
@authorized_user(allowed_roles=["customer"])
def ProcessOrder(request):
    transaction_id=datetime.now().timestamp()
    data=json.loads(request.body)

    if not request.user.is_staff:
        customer,created=Customer.objects.get_or_create(user=request.user)
        order,created=Order.objects.get_or_create(customer=customer,status="Open")

        total=Decimal(data["user"]["total"]) # convert string to decimal type using decimal module so that the cartitem
        order.transaction_id=transaction_id     # would be reset to 0 after the payment has been made

        if total==order.get_cart_total:
            order.status="Complete"
            items=order.cartitem_set.all()

            for item in items:
                product=Product.objects.get(name=item.product.name)
                product.sales = item.product.sales + item.quantity
                product.stocks = item.product.stocks - item.quantity
                product.save()

        order.save()


        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data["shipping"]["address"],
                city=data["shipping"]["city"],
                state=data["shipping"]["state"],
                zipcode=data["shipping"]["zipcode"]
            )
    else:
        print("User is not logged in.")

    return JsonResponse("Payment submitted.",safe=False)


def product_details(request,pk):
    year=date.today().year

    if request.user.is_authenticated and not request.user.is_staff: # meaning user is authenticated but not admin
        customer,created=Customer.objects.get_or_create(user=request.user)
        order,created=Order.objects.get_or_create(customer=customer,status="Open")
        items=order.cartitem_set.all() # 1-to-many relationship between order and cartitem models
        cartitems=order.get_cart_items
    else:
        items=[]
        order={
            "get_cart_total":0,
            "get_cart_items":0
        }
        cartitems=order["get_cart_items"]

    product=Product.objects.get(pk=pk)
    context={"items":items,"order":order,"cartitems":cartitems,"year":year,"product":product}
    return render(request,"store/product_details.html",context)


@login_required
@authorized_user(allowed_roles=["admin"])
def admin_dashboard(request):
    year = date.today().year

    products = Product.objects.all().order_by("stocks")
    p = Paginator(products, 3)
    page = request.GET.get("page")
    products = p.get_page(page)
    nums = "a" * products.paginator.num_pages
    count = len(products)

    orders_pending = Order.objects.filter(status="Complete").count()
    orders_delivered=Order.objects.filter(status="Shipped Out").count()
    count_orders = Order.objects.filter(Q(status="Complete") | Q(status="Shipped Out")).count()

    orders=Order.objects.filter(status="Complete").order_by("-date_created")[:5]
    cartitems=CartItem.objects.filter(order__status="Complete").order_by("-date_added")

    context = {"products": products, "nums": nums, "year":year, "count":count,"count_orders":count_orders,
               "orders_delivered":orders_delivered,"orders_pending":orders_pending,"orders":orders,"items":cartitems}
    return render(request,"store/admin_dashboard.html",context)



@login_required
@admin_only
def order_details(request,pk):
    year = date.today().year

    products = Product.objects.all().order_by("stocks")
    p = Paginator(products, 3)
    page = request.GET.get("page")
    products = p.get_page(page)
    nums = "a" * products.paginator.num_pages
    count = len(products)

    orders_pending = Order.objects.filter(status="Complete").count()
    orders_delivered = Order.objects.filter(status="Shipped Out").count()
    count_orders = Order.objects.filter(Q(status="Complete") | Q(status="Shipped Out")).count()

    orders = Order.objects.filter(status="Complete").order_by("-date_created")[:5]
    cartitems=CartItem.objects.filter(order__pk=pk).order_by("-date_added")
    order=Order.objects.get(pk=pk)

    context = {"products": products, "nums": nums, "year":year, "count":count,"count_orders":count_orders,
               "orders_delivered":orders_delivered,"orders_pending":orders_pending,"orders":orders,"items":cartitems,
               "order":order}
    return render(request,"store/order_details.html",context)


@login_required
@admin_only
def order_update(request,pk):
    year = date.today().year

    products = Product.objects.all().order_by("stocks")
    p = Paginator(products, 3)
    page = request.GET.get("page")
    products = p.get_page(page)
    nums = "a" * products.paginator.num_pages
    count = len(products)

    orders_pending = Order.objects.filter(status="Complete").count()
    orders_delivered = Order.objects.filter(status="Shipped Out").count()
    count_orders = Order.objects.filter(Q(status="Complete") | Q(status="Shipped Out")).count()

    orders=Order.objects.filter(status="Complete").order_by("-date_created")[:5]
    cartitems=CartItem.objects.filter(order__pk=pk).order_by("-date_added")
    order = Order.objects.get(pk=pk)

    form=ItemUpdateForm(instance=order)

    context = {"products": products, "nums": nums, "year":year, "count":count,"count_orders":count_orders,
               "orders_delivered":orders_delivered,"orders_pending":orders_pending,"orders":orders,"items":cartitems,
               "form":form,"order":order}
    return render(request,"store/update_order.html",context)


@login_required
@admin_only
def save_order(request,pk):
    order = Order.objects.get(pk=pk)

    if request.method=="POST":
        form=ItemUpdateForm(request.POST,instance=order)
        if form.is_valid:
            form.save()
            return redirect("store:admin_dashboard")


@login_required
@admin_only
def cancel_order(request,pk):
    order=Order.objects.get(pk=pk)
    cartitems=order.cartitem_set.all()

    for item in cartitems:
        product_pk=item.product.pk
        product=Product.objects.get(pk=product_pk)
        product.stocks=product.stocks + item.quantity
        product.sales=product.sales - item.quantity

    order.status="Cancelled"
    order.save()
    return redirect("store:admin_dashboard")


@login_required
@authorized_user(allowed_roles=["customer"])
def delete_order(request,pk):
    order=Order.objects.get(pk=pk)
    cartitem=CartItem.objects.filter(order__pk=pk)

    cartitem.delete()
    order.delete()
    return redirect("store:dashboard")


@login_required
@admin_only
def add_product(request):
    form=ProductForm()
    year = date.today().year

    if request.method=="POST":
        form=ProductForm(request.POST,request.FILES)
        if form.is_valid:
            product=form.save(commit=False)

            if "image" in request.FILES:
                product.image=request.FILES["image"]

            product.name=product.name.title() #updates the field value
            product.save()
            messages.success(request,f"{product.name.title()} product was added to the database.")
            return redirect("store:admin_dashboard")

    context={"form":form,"year":year}
    return render(request,"store/product_form.html",context)


@login_required
@admin_only
def update_product(request,pk):
    product=Product.objects.get(pk=pk)
    form=ProductForm(instance=product)
    year=date.today().year

    if request.method=="POST":
        form=ProductForm(request.POST,request.FILES,instance=product)
        product=form.save(commit=False)

        if "image" in request.FILES:
            product.image=request.FILES["image"]

        product.save()
        messages.success(request, f"Product {product.name.title()} product was added to the database.")
        return redirect("store:admin_dashboard")

    context = {"form": form, "year": year,"product":product}
    return render(request, "store/update_product_form.html", context)


@login_required
@admin_only
def delete_product(request,pk):
    year=date.today().year
    product=Product.objects.get(pk=pk)

    if request.method=="POST":
        product.image.delete()

        messages.success(request,f"{product.name.title()} has been deleted in the database.")
        product.delete()
        return redirect("store:admin_dashboard")

    context={"product":product,"year":year}
    return render(request,"store/product_confirm_delete.html",context)

@login_required
@authorized_user(allowed_roles=["customer"])
def user_profile(request):
    year=date.today().year

    if request.user.is_authenticated and not request.user.is_staff: # meaning user is authenticated but not admin
        customer,created=Customer.objects.get_or_create(user=request.user)
        order,created=Order.objects.get_or_create(customer=customer,status="Open")
        items=order.cartitem_set.all() # 1-to-many relationship between order and cartitem models
        cartitems=order.get_cart_items
    else:
        items=[]
        order={
            "get_cart_total":0,
            "get_cart_items":0
        }
        cartitems=order["get_cart_items"]

    customer=Customer.objects.get(user=request.user)
    order_completed=Order.objects.filter(status__iexact="Complete").order_by("-date_created")
    order_count=order_completed.count()
    items_completed=CartItem.objects.filter(Q(order__customer__user=request.user) & Q(order__status__iexact="Complete") | Q(order__status__iexact="Shipped Out")).order_by("-date_added")[:10]

    context={"cartitems":cartitems,"year":year,"customer":customer,"order_count":order_count,"items":items_completed,"order":order_completed}
    return render(request,"store/dashboard.html",context)