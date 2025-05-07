from django.urls import path
from .views import*
app_name = 'user'

urlpatterns = [
    path('', home, name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('users/', UserListView.as_view(), name='user_list'),
    path('admin-dashboard/users/add/', UserCreateView.as_view(), name='user_add'),
    path('admin-dashboard/users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('admin-dashboard/users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),

    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('seller-dashboard/', SellerDashboardView.as_view(), name='seller_dashboard'),
    path('consumer-dashboard/', ConsumerDashboardView.as_view(), name='consumer_dashboard'),

    path('product_list/', ProductListView.as_view(), name='product_list'),
    path('product_detail/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),  # Ensure this line is present
    path('add_product/', ProductCreateView.as_view(), name='add_product'),

    path('cart/', CartDetail.as_view(), name='cart_detail'),
    path('cart/add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/update/<int:cart_item_id>/', UpdateCartView.as_view(), name='update_cart'),

    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/', PaymentView.as_view(), name='payment'),  # Add this line
    path('payment-success/<int:order_id>/', PaymentSuccessView.as_view(), name='payment_success'),
    path('invoice/<int:order_id>/', GenerateInvoiceView.as_view(), name='invoice_pdf'),
    path('test-invoice/<int:order_id>/', test_invoice, name='test-invoice'),
    path('my-orders/', MyOrdersView.as_view(), name='my_orders'),

    path('contact/', ContactView.as_view(), name='contact'),
    path('about/', AboutView.as_view(), name='about'),
    path('ai-chat/', AIChatView.as_view(), name='ai_chat'),
]
