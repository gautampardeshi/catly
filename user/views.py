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
from .models import *
from django.views.generic import ListView
from .models import Product, Cart, CartItem
import google.generativeai as genai
from weasyprint import HTML
from .forms import SignUpForm, ContactForm, CheckoutForm
from django.views import View
from django.http import HttpResponse
from weasyprint import HTML
import tempfile
from django.views import View
from django.views.generic import TemplateView
from django.views import View
from django.views import View
from django.contrib import messages
import razorpay
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import CustomUser
from .forms import SignUpForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.shortcuts import render
from .models import product_Order, OrderItem
from django.views import View
from .models import Product
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Product
from .forms import ProductForm
from django.views import View
from .models import Product, product_Order, OrderItem
from django.http import HttpResponse
from weasyprint import HTML
import tempfile
from django.contrib import messages
from django.conf import settings
import razorpay
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from weasyprint import HTML
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import base64
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.http import HttpResponse
import weasyprint
import tempfile
from django.template.loader import get_template
# ✅ User Dashboard View (for logged-in user)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from .models import Contact
from .forms import ContactForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import product_Order  # Make sure this model is correctly defined

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
            elif user.role == 'USER':
                return redirect('user:user_dashboard')
            elif user.role == 'CONSUMER':
                return redirect('user:consumer_dashboard')
            else:
                logout(request)
                return render(request, 'accounts/login.html', {'error': 'Invalid role assigned to the user.'})
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid username or password.'})


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse_lazy('user:login'))


class UserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'

class UserCreateView(LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = SignUpForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user_list')

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = SignUpForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user_list')

class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')



@method_decorator(login_required, name='dispatch')
class AdminDashboardView(View):
    def get(self, request):
        orders = product_Order.objects.all().order_by('-created_at')
        total_orders = orders.count()
        # Remove pending_orders and delivered_orders count if status field doesn't exist
        context = {
            'orders': orders,
            'total_orders': total_orders,
        }
        return render(request, 'accounts/admin_dashboard.html', context)

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from datetime import timedelta

def AnalyticsView(request):
    # Last 6 months
    six_months_ago = now() - timedelta(days=180)
    orders = product_Order.objects.filter(created_at__gte=six_months_ago)

    # Total Orders & Revenue
    total_orders = orders.count()
    total_revenue = orders.aggregate(total=Sum('total_price'))['total'] or 0

    # Monthly Data for Chart
    monthly_data = (
        orders
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(order_count=Count('id'), revenue=Sum('total_price'))
        .order_by('month')
    )

    months = [entry['month'].strftime('%b') for entry in monthly_data]
    order_counts = [entry['order_count'] for entry in monthly_data]
    revenues = [float(entry['revenue']) for entry in monthly_data]

    # Pie Chart Data (status-wise)
    status_data = orders.values('status').annotate(count=Count('id'))
    status_dict = {item['status']: item['count'] for item in status_data}

    completed_orders = status_dict.get('Completed', 0)
    pending_orders = status_dict.get('Pending', 0)
    cancelled_orders = status_dict.get('Cancelled', 0)

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'months': months,
        'order_counts': order_counts,
        'revenues': revenues,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'cancelled_orders': cancelled_orders,
        'pending_orders': product_Order.objects.filter(status='Pending').count(),
        'shipped_orders': product_Order.objects.filter(status='Shipped').count(),
        'delivered_orders': product_Order.objects.filter(status='Delivered').count()
    }
    return render(request, 'accounts/admin_analytics.html', context)

from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
import tempfile
from django.db.models import Sum

def generate_pdf_report(request):
    total_orders = product_Order.objects.count()
    total_revenue = product_Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    pending_orders = product_Order.objects.filter(status='Pending').count()
    shipped_orders = product_Order.objects.filter(status='Shipped').count()
    delivered_orders = product_Order.objects.filter(status='Delivered').count()
    # cancelled_orders = product_Order.objects.filter(status='Cancelled').count()

    html_string = render_to_string('accounts/admin_report.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        # 'cancelled_orders': cancelled_orders,
    })

    html = HTML(string=html_string)
    result = html.write_pdf()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=catly_admin_report.pdf'
    response.write(result)
    return response


@method_decorator(login_required, name='dispatch')
class AdminOrderListView(View):
    def get(self, request):
        orders = product_Order.objects.all().order_by('-created_at')
        return render(request, 'accounts/admin_order_list.html', {'orders': orders})

    def post(self, request):
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        if order_id and new_status:
            order = get_object_or_404(product_Order, id=order_id)
            if new_status in dict(product_Order.STATUS_CHOICES).keys():
                order.status = new_status
                order.save()
                messages.success(request, f"✅ Order #{order.id} updated to '{new_status}'")
            else:
                messages.error(request, "⚠️ Invalid status value.")
        else:
            messages.error(request, "⚠️ Missing order ID or status.")

        return redirect('admin_order_list')

# accounts/views.py


def generate_invoice_pdf(request, order_id):
    order = product_Order.objects.get(id=order_id)
    template = get_template('accounts/invoice_template.html')  # aapka invoice template
    html = template.render({'order': order})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'
    
    weasyprint.HTML(string=html).write_pdf(response)
    return response


class AdminContactListView(ListView):
    model = Contact
    template_name = 'accounts/contact_messages.html'
    context_object_name = 'contacts'
    ordering = ['-created_at']


def update_order_status(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(product_Order, id=order_id)
        status = request.POST.get("status")
        if status in ['Pending', 'Shipped', 'Delivered']:
            order.status = status
            order.save()
        return redirect('user:all_orders')

def all_orders_view(request):
    orders = product_Order.objects.all().order_by('-id')  # latest order first
    return render(request, 'accounts/admin_order_list.html', {'orders': orders})


class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/user_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        orders = product_Order.objects.filter(user=self.request.user).order_by('-created_at')

        context['recent_orders'] = orders[:5]
        context['total_orders'] = orders.count()
        context['total_spent'] = sum(order.total_price for order in orders)
        context['pending_orders'] = orders.filter(status='Pending').count()
        context['invoices_generated'] = orders.count()  # adjust if you add invoices later

        return context

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
            genai.configure(api_key="AIzaSyDkZs1aB4c2fWorZNKK81uXyREk8GRfSqo")
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
        # Save to DB
        form.save()

        # Send Email
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


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'accounts/add_product.html'
    
    def form_valid(self, form):
        product = form.save()  # Product ko save karein
        return redirect('user:product_detail', pk=product.pk)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'accounts/product_detail.html'  # Ensure this template exists in your templates folder
    context_object_name = 'product'


class ProductListView(ListView):
    model = Product
    template_name = 'accounts/product_list.html'
    context_object_name = 'object_list'

class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
        cart_item_qs = CartItem.objects.filter(cart=cart, product=product)
        if cart_item_qs.exists():
            cart_item = cart_item_qs.first()
            cart_item.quantity += 1
            cart_item.save()
        else:
            CartItem.objects.create(cart=cart, product=product, quantity=1)

        return redirect('user:cart_detail')


class RemoveFromCartView(View):
    def post(self, request, cart_item_id):
        session_key = request.session.session_key
        if not session_key:
            return redirect('user:cart_detail')

        cart = get_object_or_404(Cart, session_key=session_key, user=None)
        CartItem.objects.filter(id=cart_item_id, cart=cart).delete()
        return redirect('user:cart_detail')


class UpdateCartView(View):
    def post(self, request, cart_item_id):
        session_key = request.session.session_key
        if not session_key:
            return redirect('user:cart_detail')  # Or handle error

        cart = get_object_or_404(Cart, session_key=session_key, user=None)
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

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



class CheckoutView(View):
    def get(self, request):
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        cart = get_object_or_404(Cart, session_key=session_key, user=None)
        cart_items = CartItem.objects.filter(cart=cart)

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        total_amount_in_paise = int(total_price * 100)

        if total_amount_in_paise < 100:
            messages.error(request, "Your order amount must be at least ₹1 to proceed.")
            return redirect("user:cart_detail")

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        payment = client.order.create({
            'amount': total_amount_in_paise,
            'currency': 'INR',
            'payment_capture': 1
        })

        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'razorpay_order_id': payment['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'total_amount_in_paise': total_amount_in_paise,
        }
        return render(request, 'accounts/checkout.html', context)

    def post(self, request):
        session_key = request.session.session_key
        if not session_key:
            messages.error(request, "Session expired. Please try again.")
            return redirect("user:cart_detail")

        cart = get_object_or_404(Cart, session_key=session_key, user=None)
        cart_items = CartItem.objects.filter(cart=cart)

        # Fetch form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone_number')
        payment_id = request.POST.get('razorpay_payment_id')
        email = request.POST.get('email')

        total_price = sum(item.product.price * item.quantity for item in cart_items)

        order = product_Order.objects.create(
            user=request.user if request.user.is_authenticated else None,  # ✅ yeh zaroor likh!
            session_key=session_key,
            email=email,
            first_name=first_name,
            last_name=last_name,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            phone_number=phone,
            razorpay_order_id=payment_id,
            total_price=total_price
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()
        return redirect('user:generate_invoice', order_id=order.id)


class PaymentView(View):
    def get(self, request):
        order_id = request.session.get('order_id')
        order = get_object_or_404(product_Order, id=order_id)
        return render(request, 'accounts/payment.html', {'order': order})

    def post(self, request):
        order_id = request.session.get('order_id')
        order = get_object_or_404(product_Order, id=order_id)
        # Simulating payment success
        if order:
            order.payment_status = 'Paid'
            order.save()
            return redirect('user:payment_success', order.id)

class PaymentSuccessView(View):
    def get(self, request, order_id):
        order = get_object_or_404(product_Order, id=order_id)
        return render(request, 'accounts/payment_success.html', {'order': order})
 
class GenerateInvoiceView(View):
    def get(self, request, order_id):
        order = get_object_or_404(product_Order, id=order_id)
        order_items = OrderItem.objects.filter(order=order)

        for item in order_items:
            item.subtotal = item.price * item.quantity

        # Barcode generation
        ean = barcode.get('code128', str(order.id), writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
        barcode_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Render HTML with barcode
        html_string = render_to_string('accounts/invoice.html', {
            'order': order,
            'order_items': order_items,
            'barcode_base64': barcode_base64,
        })

        # Generate PDF
        pdf_file = HTML(string=html_string).write_pdf()

        # Email sending
        if order.email:  # Assuming you have an email field in product_Order
            email = EmailMessage(
                subject=f"Invoice for Order #{order.id}",
                body="Dear Customer,\n\nPlease find attached your invoice.\n\nThank you for shopping with us!",
                from_email="noreply@catly.com",
                to=[order.email]
            )
            email.attach(f"invoice_{order.id}.pdf", pdf_file, 'application/pdf')
            email.send()

        # Return PDF to browser
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=invoice_{order.id}.pdf'
        return response

class MyOrdersView(LoginRequiredMixin, ListView):
    model = product_Order
    template_name = "user/my_orders.html"  # Adjust if different
    context_object_name = "orders"

    def get_queryset(self):
        return product_Order.objects.filter(user=self.request.user).order_by("-created_at")

def test_invoice(request, order_id):
    order = get_object_or_404(product_Order, id=order_id)
    return render(request, 'accounts/invoice.html', {'order': order})

