USERS/ADMIN.PY:

from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser, MemberApplication
from posts.models import Post, DonationRequest, Comment

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_member', 'is_verified')
    list_filter = ('is_member', 'is_verified')

@admin.register(MemberApplication)
class MemberApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'application_date', 'is_approved')
    list_filter = ('is_approved',)
    actions = ['approve_applications']

    def approve_applications(self, request, queryset):
        for application in queryset:
            application.is_approved = True
            application.user.is_verified = True
            application.user.is_member = True
            application.user.save()
            application.save()
        self.message_user(request, f'{queryset.count()} applications were successfully approved.')
    approve_applications.short_description = "Approve selected applications"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('review-applications/', self.admin_site.admin_view(self.review_applications_view), name='review_applications'),
        ]
        return custom_urls + urls

    def review_applications_view(self, request):
        applications = MemberApplication.objects.filter(is_approved=False)
        if request.method == 'POST':
            approved_ids = request.POST.getlist('approve')
            for app_id in approved_ids:
                application = MemberApplication.objects.get(id=app_id)
                application.is_approved = True
                application.user.is_verified = True
                application.user.is_member = True
                application.user.save()
                application.save()
            messages.success(request, f'{len(approved_ids)} applications were successfully approved.')
            return redirect('..')
        return render(request, 'admin/review_applications.html', {'applications': applications})

class DonationRequestInline(admin.StackedInline):
    model = DonationRequest
    extra = 0

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_type', 'is_approved', 'created_at')
    list_filter = ('post_type', 'is_approved', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'author_name')
    inlines = [DonationRequestInline]

    def get_inline_instances(self, request, obj=None):
        if obj and obj.post_type == 'donation':
            return [inline(self.model, self.admin_site) for inline in self.inlines]
        return []

@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ('post', 'estimated_cost', 'prosthetic_type')
    list_filter = ('prosthetic_type',)
    search_fields = ('post__title', 'prosthetic_type')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'author_name')


POSTS/ADMIN.PY

from django.contrib import admin
from .models import Post, DonationRequest, Comment

class DonationRequestInline(admin.StackedInline):
    model = DonationRequest
    
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_type', 'is_approved', 'created_at')
    list_filter = ('post_type', 'is_approved')
    search_fields = ('title', 'content', 'author__username', 'author_name')
    actions = ['approve_posts']
    inlines = [DonationRequestInline]
    def get_author(self, obj):
        if obj.author:
            return obj.author.username
        return obj.author_name or 'Unknown'
    get_author.short_description = 'Author'
    
    def approve_posts(self, request, queryset):
        queryset.update(is_approved=True)
    approve_posts.short_description = "Approve selected posts"

@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ('post', 'estimated_cost', 'prosthetic_type')


    