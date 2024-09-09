from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
class Post(models.Model):
    POST_TYPE_CHOICES = [
        ('regular', 'Regular Post'),
        ('donation', 'Donation Request'),
    ]
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    author_name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='regular')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)  # Add this line
    post_type = models.CharField(max_length=20, choices=[('regular', 'Regular'), ('donation', 'Donation')], default='regular')

    def __str__(self):
            if self.author:
                return f"{self.title} by {self.author.username}"
            else:
                return f"{self.title} by {self.author_name or 'Unknown'}"
        
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    author_name = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author_name or self.author.username} on {self.post.title}"
    
class DonationRequest(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='donation_details')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    prosthetic_type = models.CharField(max_length=100)
    measurements = models.TextField()

    def __str__(self):
        return f"Donation Request for {self.post.title}"