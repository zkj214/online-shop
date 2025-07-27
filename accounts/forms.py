from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from store.models import Customer,CartItem

User=get_user_model()

class CreateUserForm(UserCreationForm):
    password1=forms.CharField(widget=forms.TextInput)

    class Meta:
        model=User
        fields=("username","email","password1","password2")


class CustomerForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={"placeholder":""}))
    email=forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":""}))
    address=forms.CharField(widget=forms.TextInput(attrs={"placeholder":""}))
    phone=forms.CharField(widget=forms.TextInput(attrs={"placeholder":""}))
    class Meta:
        model=Customer
        fields="__all__"
        exclude=["user","profile_pic"]


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model=Customer
        fields=["profile_pic"]

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["profile_pic"].label=""


class RegisterCustomerForm(forms.ModelForm):
    class Meta:
        model=Customer
        fields=["name"]