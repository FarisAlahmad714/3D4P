from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class EmailService:
    """
    Centralized email service for the 3D4P platform.
    Handles all automated email notifications.
    """
    
    @staticmethod
    def send_email(subject, message, recipient_list, html_message=None, fail_silently=True):
        """
        Send email with error handling and logging
        """
        try:
            if not settings.EMAIL_HOST_USER:
                logger.warning("Email not configured - skipping email send")
                return False
                
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=fail_silently
            )
            logger.info(f"Email sent successfully to {recipient_list}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(user):
        """
        Send welcome email to new users
        """
        subject = "Welcome to 3D4P - Prosthetics for Palestine"
        
        context = {
            'user': user,
            'site_name': '3D4P - Prosthetics for Palestine',
            'login_url': f"{settings.SITE_URL}/users/login/",
            'faq_url': f"{settings.SITE_URL}/support/faq/",
        }
        
        html_message = render_to_string('emails/welcome_email.html', context)
        plain_message = strip_tags(html_message)
        
        return EmailService.send_email(
            subject=subject,
            message=plain_message,
            recipient_list=[user.email],
            html_message=html_message
        )
    
    @staticmethod
    def send_verification_status_email(user, status, reason=None):
        """
        Send verification status notification (approved/rejected)
        """
        if status == 'approved':
            subject = "✅ Your Account Has Been Verified - You Can Now Create Requests"
            template = 'emails/verification_approved.html'
        else:
            subject = "⚠️ Additional Documentation Required for Verification"
            template = 'emails/verification_rejected.html'
        
        context = {
            'user': user,
            'status': status,
            'reason': reason,
            'site_name': '3D4P - Prosthetics for Palestine',
            'contact_url': f"{settings.SITE_URL}/support/contact/",
            'dashboard_url': f"{settings.SITE_URL}/users/profile/{user.username}/",
        }
        
        html_message = render_to_string(template, context)
        plain_message = strip_tags(html_message)
        
        return EmailService.send_email(
            subject=subject,
            message=plain_message,
            recipient_list=[user.email],
            html_message=html_message
        )
    
    @staticmethod
    def send_donation_confirmation_email(donation):
        """
        Send donation confirmation to donor
        """
        subject = f"💝 Thank You for Your Donation - ${donation.amount}"
        
        context = {
            'donation': donation,
            'post': donation.post,
            'donor_name': donation.donor_name or 'Anonymous Donor',
            'site_name': '3D4P - Prosthetics for Palestine',
            'post_url': f"{settings.SITE_URL}/posts/{donation.post.id}/",
            'receipt_url': f"{settings.SITE_URL}/donations/{donation.id}/",
        }
        
        html_message = render_to_string('emails/donation_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        return EmailService.send_email(
            subject=subject,
            message=plain_message,
            recipient_list=[donation.donor_email],
            html_message=html_message
        )
    
    @staticmethod
    def send_donation_received_email(post_author, donation):
        """
        Send notification to post author when they receive a donation
        """
        subject = f"🎉 You Received a ${donation.amount} Donation!"
        
        context = {
            'user': post_author,
            'donation': donation,
            'post': donation.post,
            'donor_name': donation.donor_name if not donation.is_anonymous else 'Anonymous Donor',
            'site_name': '3D4P - Prosthetics for Palestine',
            'post_url': f"{settings.SITE_URL}/posts/{donation.post.id}/",
            'dashboard_url': f"{settings.SITE_URL}/users/profile/{post_author.username}/",
        }
        
        html_message = render_to_string('emails/donation_received.html', context)
        plain_message = strip_tags(html_message)
        
        return EmailService.send_email(
            subject=subject,
            message=plain_message,
            recipient_list=[post_author.email],
            html_message=html_message
        )
    
    @staticmethod
    def send_post_approved_email(user, post):
        """
        Send notification when user's post is approved by admin
        """
        subject = "✅ Your Request Has Been Approved and Published"
        
        context = {
            'user': user,
            'post': post,
            'site_name': '3D4P - Prosthetics for Palestine',
            'post_url': f"{settings.SITE_URL}/posts/{post.id}/",
            'dashboard_url': f"{settings.SITE_URL}/users/profile/{user.username}/",
        }
        
        html_message = render_to_string('emails/post_approved.html', context)
        plain_message = strip_tags(html_message)
        
        return EmailService.send_email(
            subject=subject,
            message=plain_message,
            recipient_list=[user.email],
            html_message=html_message
        )
    
    @staticmethod
    def send_post_rejected_email(user, post, reason=None):
        """
        Send notification when user's post is rejected by admin
        """
        subject = "⚠️ Your Request Needs Revision"
        
        context = {
            'user': user,
            'post': post,
            'reason': reason,
            'site_name': '3D4P - Prosthetics for Palestine',
            'contact_url': f"{settings.SITE_URL}/support/contact/",
            'create_post_url': f"{settings.SITE_URL}/posts/select-type/",
        }
        
        html_message = render_to_string('emails/post_rejected.html', context)
        plain_message = strip_tags(html_message)
        
        return EmailService.send_email(
            subject=subject,
            message=plain_message,
            recipient_list=[user.email],
            html_message=html_message
        )
    
    @staticmethod
    def send_admin_notification_email(subject, message, urgent=False):
        """
        Send notification to all admin users
        """
        admin_users = User.objects.filter(is_staff=True, email__isnull=False)
        admin_emails = [user.email for user in admin_users if user.email]
        
        if not admin_emails:
            logger.warning("No admin emails configured for notifications")
            return False
        
        priority = "🚨 URGENT: " if urgent else "📢 "
        full_subject = f"{priority}{subject}"
        
        context = {
            'subject': subject,
            'message': message,
            'site_name': '3D4P - Prosthetics for Palestine',
            'admin_url': f"{settings.SITE_URL}/admin-dashboard/",
            'urgent': urgent,
        }
        
        html_message = render_to_string('emails/admin_notification.html', context)
        plain_message = strip_tags(html_message)
        
        return EmailService.send_email(
            subject=full_subject,
            message=plain_message,
            recipient_list=admin_emails,
            html_message=html_message
        )
    
    @staticmethod
    def send_new_user_admin_notification(user):
        """
        Notify admins when new user registers
        """
        subject = f"New User Registration: {user.username}"
        message = f"""
        A new user has registered on the platform:
        
        Username: {user.username}
        Email: {user.email}
        Registration Date: {user.date_joined}
        
        Please review their verification application when submitted.
        """
        
        return EmailService.send_admin_notification_email(subject, message)
    
    @staticmethod
    def send_new_post_admin_notification(post):
        """
        Notify admins when new post is created (pending approval)
        """
        subject = f"New {post.post_type.title()} Post Pending Review"
        message = f"""
        A new {post.post_type} post has been submitted and needs review:
        
        Title: {post.title}
        Author: {post.author.username if post.author else post.author_name}
        Type: {post.post_type}
        Created: {post.created_at}
        
        Please review and approve/reject in the admin dashboard.
        """
        
        return EmailService.send_admin_notification_email(subject, message)
    
    @staticmethod
    def send_goal_reached_email(post, goal):
        """
        Send notification when donation goal is reached
        """
        # Notify post author
        if post.author and post.author.email:
            subject = "🎉 Congratulations! Your Donation Goal Has Been Reached!"
            
            context = {
                'user': post.author,
                'post': post,
                'goal': goal,
                'site_name': '3D4P - Prosthetics for Palestine',
                'post_url': f"{settings.SITE_URL}/posts/{post.id}/",
            }
            
            html_message = render_to_string('emails/goal_reached.html', context)
            plain_message = strip_tags(html_message)
            
            EmailService.send_email(
                subject=subject,
                message=plain_message,
                recipient_list=[post.author.email],
                html_message=html_message
            )
        
        # Notify admins
        admin_message = f"""
        Great news! A donation goal has been reached:
        
        Post: {post.title}
        Author: {post.author.username if post.author else post.author_name}
        Goal Amount: ${goal.goal_amount}
        Total Raised: ${goal.current_amount}
        
        This is a success story for the platform!
        """
        
        return EmailService.send_admin_notification_email(
            "🎉 Donation Goal Reached!", 
            admin_message
        )