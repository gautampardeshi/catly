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
    @method_decorator(login_required)
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
        cart_item.save()

        return redirect('user:cart_detail')


class RemoveFromCartView(View):
    @method_decorator(login_required)
    def post(self, request, cart_item_id):
        CartItem.objects.filter(id=cart_item_id).delete()
        return redirect('user:cart_detail')


class UpdateCartView(View):
    @method_decorator(login_required)
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
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        total_price = 0
        for item in cart_items:
            item.subtotal = item.product.price * item.quantity
            total_price += item.subtotal

        context['cart_items'] = cart_items
        context['total_price'] = total_price
        return context

class CheckoutView(View):
    def get(self, request):
        form = CheckoutForm()
        return render(request, 'accounts/checkout.html', {'form': form})

    def post(self, request):
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # You can store this in session or save as address object
            request.session['checkout_data'] = form.cleaned_data
            return redirect('user:payment')
        return render(request, 'accounts/checkout.html', {'form': form})

class PaymentView(View):
    def get(self, request):
        # Render the payment page
        return render(request, 'accounts/payment.html')
    
class PaymentSuccessView(View):
    def get(self, request):
        order_id = request.GET.get('order_id')
        return render(request, 'accounts/payment_success.html', {'order_id': order_id})

class GenerateInvoiceView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        html_content = render_to_string('accounts/invoice.html', {'order': order})
        pdf = HTML(string=html_content).write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
        return response


class MyOrdersView(View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        return render(request, 'accounts/my_orders.html', {'orders': orders})


