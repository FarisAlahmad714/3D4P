from django.urls import path
from .views import SignUpView, CustomLoginView, profile, custom_logout, application_status, member_only_view
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile_view, name='user_profile'),
    path('application-status/', views.application_status, name='application_status'),
    path('member-only/', views.member_only_view, name='member_only'),
]