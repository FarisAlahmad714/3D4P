from django.urls import path
from . import views

urlpatterns = [
    # Main donation pages
    path('', views.donation_list, name='donation_list'),
    path('donate/<int:post_id>/', views.donate_to_post, name='donate_to_post'),
    path('success/<uuid:donation_id>/', views.donation_success, name='donation_success'),
    
    # User donation management
    path('history/', views.donation_history, name='donation_history'),
    path('detail/<uuid:donation_id>/', views.donation_detail, name='donation_detail'),
    
    # Quick donation API
    path('quick/<int:post_id>/', views.quick_donate, name='quick_donate'),
    
    # Stripe webhook
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]