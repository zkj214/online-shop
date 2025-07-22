from django import forms
from store.models import Product,Order

class ProductForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={"placeholder":""}))
    price = forms.DecimalField(widget=forms.NumberInput(attrs={"placeholder":""})) # all numerical fields use NumberInput
    description = forms.CharField(widget=forms.Textarea(attrs={"placeholder":""}))

    class Meta:
        model=Product
        fields="__all__"
        exclude=["sales","digital"]


class ItemUpdateForm(forms.ModelForm):
    class Meta:
        model=Order
        fields=["status"]

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["status"].label=""