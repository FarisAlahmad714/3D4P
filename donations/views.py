from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from django.db import models

try:
    import stripe
    STRIPE_AVAILABLE = True
    # Configure Stripe
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

import json
import logging
from decimal import Decimal

from .models import Donation, DonationGoal, DonationComment
from .forms import DonationForm, QuickDonationForm, DonationCommentForm
from posts.models import Post

logger = logging.getLogger(__name__)

def donation_list(request):
    """List all active donation requests with goals"""
    posts_with_goals = Post.objects.filter(
        post_type='donation',
        is_approved=True,
        donation_goal__is_active=True
    ).select_related('donation_goal', 'author').prefetch_related('donations')
    
    # Add progress data
    for post in posts_with_goals:
        post.donation_goal.update_current_amount()
    
    paginator = Paginator(posts_with_goals, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'total_raised': sum(post.donation_goal.current_amount for post in posts_with_goals),
        'total_goals': sum(post.donation_goal.goal_amount for post in posts_with_goals),
    }
    return render(request, 'donations/donation_list.html', context)

def donate_to_post(request, post_id):
    """Main donation page for a specific post"""
    post = get_object_or_404(Post, id=post_id, post_type='donation', is_approved=True)
    
    # Get or create donation goal
    try:
        goal = post.donation_goal
    except DonationGoal.DoesNotExist:
        # Create default goal if none exists
        goal = DonationGoal.objects.create(
            post=post,
            goal_amount=Decimal('5000.00')  # Default goal
        )
    
    goal.update_current_amount()
    
    # Recent donations for this post
    recent_donations = post.donations.filter(
        payment_status='completed',
        is_anonymous=False
    ).select_related('donor')[:5]
    
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            return process_donation(request, post, form)
    else:
        # Pre-fill form if user is logged in
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'donor_name': request.user.get_full_name() or request.user.username,
                'donor_email': request.user.email,
            }
        form = DonationForm(initial=initial_data)
    
    context = {
        'post': post,
        'goal': goal,
        'form': form,
        'recent_donations': recent_donations,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
        'total_donors': post.donations.filter(payment_status='completed').count(),
    }
    return render(request, 'donations/donate_form.html', context)

def process_donation(request, post, form):
    """Process the donation through Stripe"""
    try:
        donation = form.save(commit=False)
        donation.post = post
        
        if request.user.is_authenticated:
            donation.donor = request.user
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            donation.ip_address = x_forwarded_for.split(',')[0]
        else:
            donation.ip_address = request.META.get('REMOTE_ADDR')
        
        donation.save()
        
        # Create Stripe Checkout Session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(donation.amount * 100),  # Convert to cents
                        'product_data': {
                            'name': f'Donation to: {post.title}',
                            'description': f'Prosthetic donation for {post.author.username if post.author else post.author_name}',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                customer_email=donation.donor_email,
                success_url=request.build_absolute_uri(
                    reverse('donation_success', kwargs={'donation_id': donation.id})
                ),
                cancel_url=request.build_absolute_uri(
                    reverse('donate_to_post', kwargs={'post_id': post.id})
                ),
                metadata={
                    'donation_id': str(donation.id),
                    'post_id': str(post.id),
                }
            )
            
            # Save session ID to donation
            donation.stripe_checkout_session_id = checkout_session.id
            donation.payment_status = 'processing'
            donation.save()
            
            return redirect(checkout_session.url)
            
        except stripe.error.StripeError as e:
            messages.error(request, f'Payment processing error: {str(e)}')
            donation.payment_status = 'failed'
            donation.save()
            return redirect('donate_to_post', post_id=post.id)
            
    except Exception as e:
        logger.error(f'Donation processing error: {str(e)}')
        messages.error(request, 'An error occurred while processing your donation.')
        return redirect('donate_to_post', post_id=post.id)

def donation_success(request, donation_id):
    """Success page after completed donation"""
    donation = get_object_or_404(Donation, id=donation_id)
    
    # Update goal amount
    if hasattr(donation.post, 'donation_goal'):
        donation.post.donation_goal.update_current_amount()
    
    context = {
        'donation': donation,
        'post': donation.post,
    }
    return render(request, 'donations/donation_success.html', context)

@login_required
def donation_history(request):
    """User's donation history"""
    donations = Donation.objects.filter(
        donor=request.user
    ).select_related('post').order_by('-created_at')
    
    paginator = Paginator(donations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate totals
    total_donated = donations.filter(payment_status='completed').aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0.00')
    
    context = {
        'donations': page_obj,
        'total_donated': total_donated,
        'completed_donations': donations.filter(payment_status='completed').count(),
    }
    return render(request, 'donations/donation_history.html', context)

def donation_detail(request, donation_id):
    """Detailed view of a single donation"""
    donation = get_object_or_404(Donation, id=donation_id)
    
    # Only show to donor or post author
    if request.user.is_authenticated and (
        donation.donor == request.user or 
        donation.post.author == request.user or
        request.user.is_staff
    ):
        context = {'donation': donation}
        return render(request, 'donations/donation_detail.html', context)
    else:
        messages.error(request, 'You do not have permission to view this donation.')
        return redirect('donation_list')

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        logger.error('Invalid payload in Stripe webhook')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.error('Invalid signature in Stripe webhook')
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_successful_payment(session)
    elif event['type'] == 'checkout.session.expired':
        session = event['data']['object']
        handle_failed_payment(session, 'expired')
    
    return HttpResponse(status=200)

def handle_successful_payment(session):
    """Handle successful Stripe payment"""
    try:
        donation_id = session['metadata']['donation_id']
        
        with transaction.atomic():
            donation = Donation.objects.get(id=donation_id)
            donation.payment_status = 'completed'
            donation.stripe_payment_intent_id = session.get('payment_intent', '')
            donation.completed_at = timezone.now()
            donation.save()
            
            # Update donation goal
            if hasattr(donation.post, 'donation_goal'):
                donation.post.donation_goal.update_current_amount()
                
            logger.info(f'Donation {donation_id} completed successfully')
            
    except Donation.DoesNotExist:
        logger.error(f'Donation {donation_id} not found for successful payment')
    except Exception as e:
        logger.error(f'Error handling successful payment: {str(e)}')

def handle_failed_payment(session, reason='failed'):
    """Handle failed Stripe payment"""
    try:
        donation_id = session['metadata']['donation_id']
        
        donation = Donation.objects.get(id=donation_id)
        donation.payment_status = 'failed' if reason != 'expired' else 'cancelled'
        donation.save()
        
        logger.info(f'Donation {donation_id} marked as {donation.payment_status}')
        
    except Donation.DoesNotExist:
        logger.error(f'Donation {donation_id} not found for failed payment')
    except Exception as e:
        logger.error(f'Error handling failed payment: {str(e)}')

@require_POST
def quick_donate(request, post_id):
    """Quick donation with preset amounts"""
    post = get_object_or_404(Post, id=post_id, post_type='donation', is_approved=True)
    
    if request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        amount = data.get('amount')
        email = data.get('email')
    else:
        amount = request.POST.get('amount')
        email = request.POST.get('email')
    
    try:
        amount = Decimal(str(amount))
        if amount < Decimal('1.00'):
            raise ValueError('Invalid amount')
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid donation amount'}, status=400)
    
    # Create donation
    donation = Donation.objects.create(
        post=post,
        donor=request.user if request.user.is_authenticated else None,
        donor_email=email,
        amount=amount,
        is_anonymous=True,
        payment_status='processing'
    )
    
    # Return checkout URL
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(amount * 100),
                    'product_data': {
                        'name': f'Quick Donation: {post.title}',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            customer_email=email,
            success_url=request.build_absolute_uri(
                reverse('donation_success', kwargs={'donation_id': donation.id})
            ),
            cancel_url=request.build_absolute_uri(
                reverse('donate_to_post', kwargs={'post_id': post.id})
            ),
        )
        
        donation.stripe_checkout_session_id = checkout_session.id
        donation.save()
        
        return JsonResponse({'checkout_url': checkout_session.url})
        
    except stripe.error.StripeError as e:
        donation.payment_status = 'failed'
        donation.save()
        return JsonResponse({'error': 'Payment processing failed'}, status=400)
