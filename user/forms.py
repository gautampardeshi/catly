from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re

class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name','last_name','username','phone_number', 'email', 'role', 'password1', 'password2')
        # phone_number = forms.CharField(max_length=15, required=False)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            if not phone_number.isdigit() or len(phone_number) < 10:
                raise forms.ValidationError("Enter a valid phone number with at least 10 digits.")
        return phone_number

from django import forms
from .models import Contact
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone_number', 'message']

class CheckoutForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), label="Address")
    city = forms.CharField(max_length=50)
    state = forms.CharField(max_length=50)
    zip_code = forms.CharField(max_length=10, label="ZIP Code")
    phone_number = forms.CharField(max_length=15)

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image']

