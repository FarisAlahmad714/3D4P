from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator

from posts.models import Post, DonationRequest
from users.models import CustomUser, MemberApplication, MemberProfile
from donations.models import Donation, DonationGoal

def is_admin(user):
    return user.is_staff and user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get key statistics
    stats = {
        'total_users': CustomUser.objects.count(),
        'total_posts': Post.objects.count(),
        'total_donations': Donation.objects.filter(payment_status='completed').count(),
        'total_raised': Donation.objects.filter(payment_status='completed').aggregate(
            total=Sum('amount'))['total'] or 0,
        'pending_posts': Post.objects.filter(is_approved=False).count(),
        'pending_members': MemberApplication.objects.filter(is_approved=False).count(),
        'active_campaigns': DonationGoal.objects.filter(is_active=True).count(),
    }
    
    # Recent activity
    recent_posts = Post.objects.select_related('author').order_by('-created_at')[:5]
    recent_donations = Donation.objects.select_related('post', 'donor').filter(
        payment_status='completed'
    ).order_by('-created_at')[:5]
    pending_posts = Post.objects.filter(is_approved=False).select_related('author')[:5]
    
    # Monthly data for charts
    now = timezone.now()
    months = []
    donation_data = []
    post_data = []
    
    for i in range(6):
        month_start = now.replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end - timedelta(days=month_end.day)
        
        months.append(month_start.strftime('%B'))
        
        monthly_donations = Donation.objects.filter(
            created_at__range=[month_start, month_end],
            payment_status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_posts = Post.objects.filter(
            created_at__range=[month_start, month_end]
        ).count()
        
        donation_data.append(float(monthly_donations))
        post_data.append(monthly_posts)
    
    # Reverse to get chronological order
    months.reverse()
    donation_data.reverse()
    post_data.reverse()
    
    context = {
        'stats': stats,
        'recent_posts': recent_posts,
        'recent_donations': recent_donations,
        'pending_posts': pending_posts,
        'chart_data': {
            'months': months,
            'donations': donation_data,
            'posts': post_data,
        }
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)

@user_passes_test(is_admin)
def admin_posts(request):
    status_filter = request.GET.get('status', 'all')
    post_type = request.GET.get('type', 'all')
    search = request.GET.get('search', '')
    
    posts = Post.objects.select_related('author').prefetch_related('donation_details', 'donation_goal')
    
    if status_filter == 'pending':
        posts = posts.filter(is_approved=False)
    elif status_filter == 'approved':
        posts = posts.filter(is_approved=True)
    
    if post_type == 'donation':
        posts = posts.filter(post_type='donation')
    elif post_type == 'regular':
        posts = posts.filter(post_type='regular')
    
    if search:
        posts = posts.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search) |
            Q(author__username__icontains=search)
        )
    
    posts = posts.order_by('-created_at')
    
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'post_type': post_type,
        'search': search,
    }
    
    return render(request, 'admin_dashboard/posts.html', context)

@user_passes_test(is_admin)
def approve_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.is_approved = True
    post.save()
    messages.success(request, f'Post "{post.title}" has been approved.')
    return redirect('admin_posts')

@user_passes_test(is_admin)
def reject_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.is_approved = False
    post.save()
    messages.warning(request, f'Post "{post.title}" has been rejected.')
    return redirect('admin_posts')

@user_passes_test(is_admin)
def admin_users(request):
    status_filter = request.GET.get('status', 'all')
    search = request.GET.get('search', '')
    
    users = CustomUser.objects.select_related('memberprofile')
    
    if status_filter == 'verified':
        users = users.filter(is_verified=True)
    elif status_filter == 'pending':
        users = users.filter(is_verified=False)
    elif status_filter == 'staff':
        users = users.filter(is_staff=True)
    
    if search:
        users = users.filter(
            Q(username__icontains=search) | 
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    users = users.order_by('-date_joined')
    
    paginator = Paginator(users, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add donation totals for each user in the current page
    for user in page_obj:
        user.total_donations = Donation.objects.filter(
            donor_email=user.email, 
            payment_status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get pending member applications
    pending_applications = MemberApplication.objects.filter(
        is_approved=False
    ).select_related('user').order_by('-application_date')[:10]
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search': search,
        'pending_applications': pending_applications,
    }
    
    return render(request, 'admin_dashboard/users.html', context)

@user_passes_test(is_admin)
def approve_member(request, application_id):
    application = get_object_or_404(MemberApplication, id=application_id)
    application.is_approved = True
    application.save()
    messages.success(request, f'Member application for {application.user.username} has been approved.')
    return redirect('admin_users')

@user_passes_test(is_admin)
def reject_member(request, application_id):
    application = get_object_or_404(MemberApplication, id=application_id)
    application.is_approved = False
    application.save()
    messages.warning(request, f'Member application for {application.user.username} has been rejected.')
    return redirect('admin_users')

@user_passes_test(is_admin)
def admin_donations(request):
    status_filter = request.GET.get('status', 'all')
    search = request.GET.get('search', '')
    
    donations = Donation.objects.select_related('post', 'donor').order_by('-created_at')
    
    if status_filter != 'all':
        donations = donations.filter(payment_status=status_filter)
    
    if search:
        donations = donations.filter(
            Q(post__title__icontains=search) |
            Q(donor_email__icontains=search) |
            Q(donor_name__icontains=search)
        )
    
    paginator = Paginator(donations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    donation_stats = {
        'total_amount': Donation.objects.filter(payment_status='completed').aggregate(
            total=Sum('amount'))['total'] or 0,
        'total_donations': Donation.objects.filter(payment_status='completed').count(),
        'pending_amount': Donation.objects.filter(payment_status='pending').aggregate(
            total=Sum('amount'))['total'] or 0,
        'average_donation': Donation.objects.filter(payment_status='completed').aggregate(
            avg=Avg('amount'))['avg'] or 0,
    }
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search': search,
        'donation_stats': donation_stats,
    }
    
    return render(request, 'admin_dashboard/donations.html', context)

@user_passes_test(is_admin)
def admin_analytics(request):
    # Time-based analytics
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    last_7_days = now - timedelta(days=7)
    
    analytics = {
        'users': {
            'total': CustomUser.objects.count(),
            'new_this_month': CustomUser.objects.filter(date_joined__gte=last_30_days).count(),
            'new_this_week': CustomUser.objects.filter(date_joined__gte=last_7_days).count(),
        },
        'posts': {
            'total': Post.objects.count(),
            'this_month': Post.objects.filter(created_at__gte=last_30_days).count(),
            'donation_requests': Post.objects.filter(post_type='donation').count(),
            'regular_posts': Post.objects.filter(post_type='regular').count(),
        },
        'donations': {
            'total_amount': Donation.objects.filter(payment_status='completed').aggregate(
                total=Sum('amount'))['total'] or 0,
            'this_month_amount': Donation.objects.filter(
                payment_status='completed', 
                created_at__gte=last_30_days
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'total_count': Donation.objects.filter(payment_status='completed').count(),
            'this_month_count': Donation.objects.filter(
                payment_status='completed',
                created_at__gte=last_30_days
            ).count(),
        }
    }
    
    # Top donors
    top_donors = Donation.objects.filter(
        payment_status='completed',
        is_anonymous=False
    ).values('donor_email', 'donor_name').annotate(
        total_donated=Sum('amount'),
        donation_count=Count('id')
    ).order_by('-total_donated')[:10]
    
    # Most funded campaigns
    top_campaigns = DonationGoal.objects.select_related('post').filter(
        current_amount__gt=0
    ).order_by('-current_amount')[:10]
    
    context = {
        'analytics': analytics,
        'top_donors': top_donors,
        'top_campaigns': top_campaigns,
    }
    
    return render(request, 'admin_dashboard/analytics.html', context)