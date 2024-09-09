from django.contrib import admin
from .models import Post, DonationRequest

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