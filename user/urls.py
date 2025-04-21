from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    home,
    SignupView,
    LoginView,
    CustomLogoutView,
    AdminDashboardView,
    SellerDashboardView,
    ConsumerDashboardView,
    cart_detail,
    AIChatView,
    ContactView
    )

app_name = 'user'

urlpatterns = [
    path('', home, name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('login/admin_dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('seller/dashboard/', SellerDashboardView.as_view(), name='seller_dashboard'),
    path('consumer_dashboard', ConsumerDashboardView.as_view(), name='consumer_dashboard'),
    path('logout', CustomLogoutView.as_view(), name='logout'),
    path('cart/', cart_detail, name='cart_detail'),
    path('ai-chat/', AIChatView.as_view(), name='ai_chat'),
    path("accounts/contact/", ContactView.as_view(), name="contact"),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

