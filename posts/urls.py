from django.urls import path ,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('create/', views.select_post_type, name='select_post_type'),
    path('create/regular/', views.create_regular_post, name='create_regular_post'),
    path('create/donation/', views.create_donation_request, name='create_donation_request'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)