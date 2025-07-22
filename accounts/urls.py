from django.urls import path
from accounts.views import *
from django.contrib.auth.views import PasswordResetView,PasswordResetDoneView,PasswordResetConfirmView,PasswordResetCompleteView
from django.urls import reverse_lazy

app_name="accounts"
urlpatterns=[
    path("login/",login_user,name="login"),
    path("register/",register_user,name="register"),
    path("logout/",logout_user,name="logout"),
    path("redirect/",login_redirect,name="redirect"),
    path("settings/",user_settings,name="settings"),
    path("delete_account/user/<int:pk>",delete_account,name="delete"),
    path("password_reset/", PasswordResetView.as_view(template_name="accounts/password_reset.html", success_url=reverse_lazy("accounts:password_reset_done")), name="password_reset"),
    path("password_reset_sent/", PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), name="password_reset_done"), #url name must be equal to the view name & template name
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html",success_url=reverse_lazy("accounts:password_reset_complete")), name="password_reset_confirm"),
    path("password_reset_complete/", PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), name="password_reset_complete"),
    path("upload_photo/",upload_photo,name="upload_pic")
]