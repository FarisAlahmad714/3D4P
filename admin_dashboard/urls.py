from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('posts/', views.admin_posts, name='admin_posts'),
    path('posts/bulk-action/', views.bulk_action_posts, name='bulk_action_posts'),
    path('posts/approve/<int:post_id>/', views.approve_post, name='approve_post'),
    path('posts/reject/<int:post_id>/', views.reject_post, name='reject_post'),
    path('users/', views.admin_users, name='admin_users'),
    path('users/approve/<int:application_id>/', views.approve_member, name='approve_member'),
    path('users/reject/<int:application_id>/', views.reject_member, name='reject_member'),
    path('donations/', views.admin_donations, name='admin_donations'),
    path('analytics/', views.admin_analytics, name='admin_analytics'),
]