from django.db import models
from django.contrib.auth import get_user_model
from posts.models import Post
from decimal import Decimal
from django.urls import reverse
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
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='donations')
    donor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    donor_name = models.CharField(max_length=100, blank=True)
    donor_email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, max_length=500)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
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

class DonationComment(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, related_name='comment')
    content = models.TextField(max_length=1000)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.donation.donor_name or 'Anonymous'}"
