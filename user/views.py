from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SignUpForm
from .models import CustomUser
from django.views.generic.edit import FormView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from django.urls import reverse_lazy
from django.views.generic import TemplateView

# Home page
def home(request):
    return render(request, 'home.html')

# Signup view
# Signup View
class SignupView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, 'accounts/signup.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user:login')  # Signup ke baad sidha login page
        return render(request, 'accounts/signup.html', {'form': form})


# Login View
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

# Logout view
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('user:login')

# Dashboards
class AdminDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/admin_dashboard.html')

class SellerDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/seller_dashboard.html')

class ConsumerDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/consumer_dashboard.html')
    
def cart_detail(request):
    return render(request, 'cart_detail.html')

from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai

class AIChatView(View):
    template_name = 'accounts/ai_chat.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        user_input = request.POST.get('message')
        try:
            genai.configure(api_key="AIzaSyAEji0WIKMslC62QrxADTvAEFRgAI2rHGc")
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

        # ✅ Make sure this is NOT commented
        send_mail(
            subject='New Contact Form Submission',
            message=f'Name: {name}\nEmail: {email}\nMessage: {message}\nphone_number:{phone_number}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.ADMIN_EMAIL],
        )

        messages.success(self.request, "Your message was submitted successfully!")
        return super().form_valid(form)

class AboutView(TemplateView):
    template_name = 'accounts/About.html'