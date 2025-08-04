from django.urls import path
from .views import *
from accounts.views import login_user

app_name="store"
urlpatterns=[
    path("",login_user,name="index"),
    path("products/",item_display,name="items"),
    path("cart/",cart,name="cart"),
    path("checkout/",checkout,name="checkout"),
    path("update_cart/",UpdateCart,name="update_cart"),
    path("process_order/",ProcessOrder,name="process_order"),
    path("search_item/",search_item,name="search_item"),
    path("product_details/product_<int:pk>",product_details,name="product_details"),
    path("admin_dashboard/",admin_dashboard,name="admin_dashboard"),
    path("add_product/",add_product,name="add_product"),
    path("update_product/<int:pk>/",update_product,name="update_product"),
    path("delete_product/<int:pk>/",delete_product,name="delete_product"),
    path("dashboard/",user_profile,name="dashboard"),
    path("order_details/<int:pk>/",order_details,name="order_details"),
    path("order_update/<int:pk>/",order_update,name="order_update"),
    path("save_order/<int:pk>/",save_order,name="save_order"),
    path("cancel_order/<int:pk>/",cancel_order,name="cancel_order"),
    path("delete_order/<int:pk>/",delete_order,name="delete_order"),
    path("about/",about,name="about")
]