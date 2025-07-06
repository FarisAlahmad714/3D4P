from django.db import models
from django.contrib.auth import get_user_model
from posts.models import Post
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
import uuid

User = get_user_model()

class Donation(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    DONATION_TYPE_CHOICES = [
        ('one_time', 'One-time'),
        ('monthly', 'Monthly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='donations')
    donor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    donor_name = models.CharField(max_length=100, blank=True)
    donor_email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, max_length=500)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPE_CHOICES, default='one_time')
    monthly_subscription = models.ForeignKey('MonthlySubscription', on_delete=models.CASCADE, null=True, blank=True, related_name='donations')
    
    # Stripe fields
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=200, blank=True)
    stripe_customer_id = models.CharField(max_length=200, blank=True)
    
    # Privacy and tracking
    is_anonymous = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_status']),
            models.Index(fields=['post', 'payment_status']),
        ]
    
    def __str__(self):
        donor_name = self.donor.username if self.donor else (self.donor_name or 'Anonymous')
        return f"${self.amount} donation to {self.post.title} by {donor_name}"
    
    def get_absolute_url(self):
        return reverse('donation_detail', kwargs={'donation_id': self.id})
    
    @property
    def is_successful(self):
        return self.payment_status == 'completed'

class DonationGoal(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='donation_goal')
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Goal: ${self.goal_amount} for {self.post.title}"
    
    @property
    def progress_percentage(self):
        if self.goal_amount == 0:
            return 0
        return min((self.current_amount / self.goal_amount) * 100, 100)
    
    @property
    def is_completed(self):
        return self.current_amount >= self.goal_amount
    
    @property
    def remaining_amount(self):
        return max(self.goal_amount - self.current_amount, Decimal('0.00'))
    
    def update_current_amount(self):
        total = self.post.donations.filter(payment_status='completed').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        self.current_amount = total
        self.save()
        return self.current_amount
    
    @property
    def monthly_donation_total(self):
        """Calculate total monthly donations for this goal"""
        return self.post.monthly_subscriptions.filter(status='active').aggregate(
            total=models.Sum('monthly_amount')
        )['total'] or Decimal('0.00')
    
    @property
    def total_monthly_supporters(self):
        """Count of active monthly supporters"""
        return self.post.monthly_subscriptions.filter(status='active').count()

class DonationComment(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, related_name='comment')
    content = models.TextField(max_length=1000)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.donation.donor_name or 'Anonymous'}"

class MonthlySubscription(models.Model):
    SUBSCRIPTION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('incomplete', 'Incomplete'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='monthly_subscriptions')
    donor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    donor_name = models.CharField(max_length=100, blank=True)
    donor_email = models.EmailField()
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Subscription details
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(default=timezone.now)
    next_billing_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Stripe subscription fields
    stripe_subscription_id = models.CharField(max_length=200, blank=True)
    stripe_customer_id = models.CharField(max_length=200, blank=True)
    stripe_price_id = models.CharField(max_length=200, blank=True)
    
    # Privacy and settings
    is_anonymous = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['donor', 'status']),
            models.Index(fields=['next_billing_date']),
        ]
    
    def __str__(self):
        donor_name = self.donor.username if self.donor else (self.donor_name or 'Anonymous')
        return f"${self.monthly_amount}/month subscription to {self.post.title} by {donor_name}"
    
    def get_absolute_url(self):
        return reverse('subscription_detail', kwargs={'subscription_id': self.id})
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def total_donated(self):
        """Calculate total amount donated through this subscription"""
        return self.donations.filter(payment_status='completed').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    @property
    def months_active(self):
        """Calculate how many months this subscription has been active"""
        if self.status == 'cancelled' and self.cancelled_at:
            end_date = self.cancelled_at
        else:
            end_date = timezone.now()
        
        delta = end_date - self.start_date
        return delta.days // 30  # Rough calculation
    
    def cancel_subscription(self):
        """Cancel the monthly subscription"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.save()
    
    def pause_subscription(self):
        """Pause the monthly subscription"""
        self.status = 'paused'
        self.save()
    
    def resume_subscription(self):
        """Resume a paused subscription"""
        if self.status == 'paused':
            self.status = 'active'
            self.save()
