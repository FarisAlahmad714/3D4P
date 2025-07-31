from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Custom error handlers (commented out for development)
# handler404 = 'utils.error_handlers.handler404'
# handler500 = 'utils.error_handlers.handler500'
# handler403 = 'utils.error_handlers.handler403'
# handler400 = 'utils.error_handlers.handler400'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('admin_dashboard.urls')),
    path('', views.home, name='home'),
    path('users/', include('users.urls')),
    path('posts/', include('posts.urls')),
    path('campaigns/', include('campaigns.urls')),
    path('donations/', include('donations.urls')),
    path('verification/', include('verification.urls')),
    
    # Support pages
    path('support/how-it-works/', views.how_it_works, name='how_it_works'),
    path('support/faq/', views.faq, name='faq'),
    path('support/contact/', views.contact_us, name='contact_us'),
    path('support/privacy-policy/', views.privacy_policy, name='privacy_policy'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)