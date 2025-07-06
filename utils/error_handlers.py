from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
import logging
import traceback

logger = logging.getLogger(__name__)

def handler404(request, exception):
    """Custom 404 error handler"""
    logger.warning(f"404 error for URL: {request.get_full_path()}")
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    """Custom 500 error handler"""
    logger.error(f"500 error on {request.get_full_path()}: {traceback.format_exc()}")
    return render(request, 'errors/500.html', status=500)

def handler403(request, exception):
    """Custom 403 error handler"""
    logger.warning(f"403 error for user {request.user} on {request.get_full_path()}")
    return render(request, 'errors/403.html', status=403)

def handler400(request, exception):
    """Custom 400 error handler"""
    logger.warning(f"400 error on {request.get_full_path()}: {str(exception)}")
    return render(request, 'errors/400.html', status=400)

class SecurityMiddleware:
    """Custom security middleware for additional protection"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log suspicious activities
        if self.is_suspicious_request(request):
            logger.warning(
                f"Suspicious request detected: {request.method} {request.get_full_path()} "
                f"from IP: {self.get_client_ip(request)}"
            )
        
        response = self.get_response(request)
        return response

    def is_suspicious_request(self, request):
        """Detect suspicious request patterns"""
        suspicious_patterns = [
            'admin/', 'wp-admin/', 'phpmyadmin/', '.env', 'config.php',
            'shell.php', 'cmd.php', 'eval(', 'system(', 'exec('
        ]
        
        path = request.get_full_path().lower()
        return any(pattern in path for pattern in suspicious_patterns)

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip