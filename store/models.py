from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Customer(models.Model):
    user=models.OneToOneField(User,blank=True,null=True,on_delete=models.CASCADE)
    name=models.CharField(null=True,max_length=100)
    email=models.EmailField(blank=True,null=True)
    address=models.CharField(max_length=100,null=True,blank=True)
    phone=models.CharField(max_length=100,null=True,blank=True)
    profile_pic=models.ImageField(default="profile2.png",blank=True,null=True,upload_to="profile_pics")

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url=self.profile_pic.url
        except:
            url="/media/profile2.png" # if there's no uploaded photo, this will show up
        return url


class Product(models.Model):
    name=models.CharField(max_length=100,null=True)
    price=models.DecimalField(max_digits=7,decimal_places=2)
    digital=models.BooleanField(default=False)
    description=models.TextField(blank=True,null=True)
    image=models.ImageField(blank=True,null=True,upload_to="uploaded_pics")
    stocks=models.PositiveIntegerField(default=10) # 0 to up numbers are positive integers
    sales=models.PositiveIntegerField(default=0)
    date_added=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url=self.image.url
        except:
            url="/static/images/placeholder.png"
        return url


class Order(models.Model):
    CATEGORY=(
        ("Open","Open"),
        ("Complete","Complete"),
        ("Shipped Out","Shipped Out"),
        ("Cancelled","Cancelled")
    )
    customer=models.ForeignKey(Customer,on_delete=models.SET_NULL,blank=True,null=True)
    status=models.CharField(default="Open",max_length=100,choices=CATEGORY)
    transaction_id=models.CharField(null=True,max_length=100)
    date_created=models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.pk)

    @property
    def shipping(self):
        shipping=True
        items=self.cartitem_set.all()

        for item in items:
            if item.product.digital:
                shipping=False

        return shipping

    @property
    def get_cart_total(self):
        items=self.cartitem_set.all() # self referring to the order model
        cart_total=sum([item.get_total_price for item in items])
        return cart_total


    @property
    def get_cart_items(self):
        items=self.cartitem_set.all() # self referring to the order model
        total_items=sum([item.quantity for item in items])
        return total_items


class CartItem(models.Model):
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,blank=True,null=True)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    quantity=models.IntegerField(default=0,blank=True,null=True)
    date_added=models.DateField(auto_now=True)

    def __str__(self):
        return str(self.date_added)

    @property
    def get_total_price(self):
        total_price=self.product.price * self.quantity
        return total_price


class ShippingAddress(models.Model):
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    customer=models.ForeignKey(Customer,on_delete=models.SET_NULL,blank=True,null=True)
    address=models.CharField(max_length=200,null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address