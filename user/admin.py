from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomUser, Product, Cart, CartItem,product_Order

admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(product_Order)
