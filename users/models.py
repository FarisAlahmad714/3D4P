from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

class CustomUser(AbstractUser):
    is_member = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username
    pass
    
class MemberApplication(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    proof_image = models.ImageField(upload_to='proof_images/')
    application_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Application for {self.user.username}"

class MemberProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_photos',  default='default.jpg')
    bio = models.TextField(max_length=500, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        MemberProfile.objects.create(user=instance)
    else:
        MemberProfile.objects.get_or_create(user=instance)
    instance.memberprofile.save()