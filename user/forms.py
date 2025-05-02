from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')

from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Your Name")
    email = forms.EmailField(label="Your Email")
    phone_number = forms.CharField(max_length=15)
    message = forms.CharField(widget=forms.Textarea, label="Your Message")

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100, label="Full Name")
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

    