# core Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from .models import Product
from django.views.generic import ListView
from .models import Product, Cart, CartItem
# third-party
import google.generativeai as genai
from weasyprint import HTML

# local imports
from .forms import SignUpForm, ContactForm, CheckoutForm
from .models import CustomUser, Product, Cart, CartItem, Order

def home(request):
    return render(request, 'home.html')

class AboutView(TemplateView):
    template_name = 'accounts/About.html'

class SignupView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, 'accounts/signup.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user:login')
        return render(request, 'accounts/signup.html', {'form': form})


class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'ADMIN':
                return redirect('user:admin_dashboard')
            elif user.role == 'SELLER':
                return redirect('user:seller_dashboard')
            elif user.role == 'CONSUMER':
                return redirect('user:consumer_dashboard')
            else:
                logout(request)
                return render(request, 'accounts/login.html', {'error': 'Invalid role assigned to the user.'})
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid username or password.'})


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('user:login')
    def get(self, request, *args, **kwargs):
        # Treat GET requests as POST to allow logout via GET
        return self.post(request, *args, **kwargs)

class AdminDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/admin_dashboard.html')

class SellerDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/seller_dashboard.html')

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product
from django.contrib import messages

class ConsumerDashboardView(LoginRequiredMixin, View):
    login_url = '/login/'  # 👈 This line ensures unauthenticated users are redirected

    def get(self, request):
        # Get all products added by the user
        user_products = Product.objects.filter(user=request.user)
        return render(request, 'accounts/consumer-dashboard.html', {'user': request.user, 'products': user_products})

    def post(self, request):
        # Handle product addition
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')

        # Create and save the new product for the logged-in user
        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            image=image,
            user=request.user
        )

        messages.success(request, 'Product added successfully!')
        return redirect('user:consumer_dashboard')

class AIChatView(View):
    template_name = 'accounts/ai_chat.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        user_input = request.POST.get('message')
        try:
            genai.configure(api_key="YOUR_API_KEY")
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(user_input)
            reply = response.text
        except Exception as e:
            reply = f"Error: {str(e)}"

        return JsonResponse({'reply': reply})

class ContactView(FormView):
    template_name = 'accounts/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('user:contact')

    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        phone_number = form.cleaned_data['phone_number']
        message = form.cleaned_data['message']

        send_mail(
            subject='New Contact Form Submission',
            message=f'Name: {name}\nEmail: {email}\nPhone: {phone_number}\nMessage: {message}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.ADMIN_EMAIL],
        )

        messages.success(self.request, "Your message was submitted successfully!")
        return super().form_valid(form)


from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Product
from .forms import ProductForm

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'accounts/add_product.html'
    
    def form_valid(self, form):
        product = form.save()  # Product ko save karein
        return redirect('user:product_detail', pk=product.pk)

# Product Detail View: Ek specific product ka detail dikhata hai.
class ProductDetailView(DetailView):
    model = Product
    template_name = 'accounts/product_detail.html'  # Ensure this template exists in your templates folder
    context_object_name = 'product'

# Product List View: Sare products ki list dikhata hai.
class ProductListView(ListView):
    model = Product
    template_name = 'accounts/product_list.html'
    context_object_name = 'object_list'

class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        # Get or create cart using session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
        cart_item.save()

        return redirect('user:cart_detail')


class RemoveFromCartView(View):
    def post(self, request, cart_item_id):
        CartItem.objects.filter(id=cart_item_id).delete()
        return redirect('user:cart_detail')


class UpdateCartView(View):
    def post(self, request, cart_item_id):
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        new_quantity = int(request.POST.get('quantity', 1))

        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item.delete()

        return redirect('user:cart_detail')


class CartDetail(TemplateView):
    template_name = 'cart_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key

        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
        cart_items = CartItem.objects.filter(cart=cart)

        total_price = 0
        for item in cart_items:
            item.subtotal = item.product.price * item.quantity
            total_price += item.subtotal

        context['cart_items'] = cart_items
        context['total_price'] = total_price
        return context 

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Product, Order, OrderItem
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile

from django.views import View
from django.shortcuts import render, redirect
from .forms import CheckoutForm
from .models import Product, Order, OrderItem

class CheckoutView(View):
    def get(self, request):
        cart = request.session.get('cart', {})
        cart_items = []
        total_price = 0

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})

        form = CheckoutForm()

        return render(request, 'accounts/checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price,
            'form': form,
        })

    def post(self, request):
        form = CheckoutForm(request.POST)

        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            phone_number = form.cleaned_data['phone_number']

            # ✅ User assign karo - ye line fix karti hai problem
            order = Order.objects.create(
                # user=request.user,  # ✅ Ye pehle None tha, ab fix hai
                full_name=full_name,
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                phone_number=phone_number,
                payment_status='Pending'
            )

            cart = request.session.get('cart', {})
            for product_id, quantity in cart.items():
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(order=order, product=product, quantity=quantity)

            request.session['order_id'] = order.id
            return redirect('user:payment')

        else:
            cart = request.session.get('cart', {})
            cart_items = []
            total_price = 0
            for product_id, quantity in cart.items():
                product = Product.objects.get(id=product_id)
                subtotal = product.price * quantity
                total_price += subtotal
                cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})

            return render(request, 'accounts/checkout.html', {
                'form': form,
                'cart_items': cart_items,
                'total_price': total_price
            })


from django.shortcuts import redirect
from django.urls import reverse

class PaymentView(View):
    def get(self, request):
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'accounts/payment.html', {'order': order})

    def post(self, request):
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        # Simulating payment success
        if order:
            order.payment_status = 'Paid'
            order.save()
            return redirect('user:payment_success', order.id)
    
from django.views.generic import TemplateView
from user.models import Order  # adjust import based on your app

class PaymentSuccessView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'accounts/payment_success.html', {'order': order})

from django.views import View
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Order
from django.http import HttpResponse
from django.template.loader import get_template
import weasyprint
from .models import Order  # adjust path to your model

class GenerateInvoiceView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        html_string = render_to_string('accounts/invoice.html', {'order': order})
        html = HTML(string=html_string)
        result = html.write_pdf()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=invoice_{order_id}.pdf'
        response.write(result)
        return response


class MyOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "user/my_orders.html"  # Adjust if different
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

def test_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'accounts/invoice.html', {'order': order})

