# posts/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Post, DonationRequest, DonationRequestImage, DonationRequestFile, Comment, PostImage  # Ensure all models are imported

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_author', 'post_type', 'is_approved', 'created_at')  # Display Post ID
    list_filter = ('post_type', 'is_approved', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'author_name')
    actions = ['approve_posts', 'deny_posts']
    inlines = [PostImageInline]

    def get_author(self, obj):
        if obj.author:
            return obj.author.username
        return obj.author_name or 'Unknown'
    get_author.short_description = 'Author'

    def approve_posts(self, request, queryset):
        queryset.update(is_approved=True)
    approve_posts.short_description = "Approve selected posts"

    def deny_posts(self, request, queryset):
        queryset.update(is_approved=False)
    deny_posts.short_description = "Deny selected posts"

class DonationRequestImageInline(admin.TabularInline):
    model = DonationRequestImage
    extra = 1

class DonationRequestFileInline(admin.TabularInline):
    model = DonationRequestFile
    extra = 1

@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_id', 'post_title', 'get_author', 'estimated_cost', 'prosthetic_type', 'is_approved', 'get_files')  # Display both IDs
    list_filter = ('post__is_approved', 'prosthetic_type')
    search_fields = ('post__title', 'post__content', 'post__author__username', 'post__author_name')
    inlines = [DonationRequestImageInline, DonationRequestFileInline]

    def post_id(self, obj):
        return obj.post.id  # Display the Post ID from the related Post object
    post_id.short_description = 'Post ID'

    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Post Title'

    def get_author(self, obj):
        return obj.post.author.username if obj.post.author else obj.post.author_name
    get_author.short_description = 'Author'

    def is_approved(self, obj):
        return obj.post.is_approved
    is_approved.boolean = True
    is_approved.short_description = 'Is Approved'

    def get_files(self, obj):
        files = obj.files.all()
        file_links = []
        for file in files:
            file_links.append(format_html('<a href="{}" target="_blank">{}</a>', file.file.url, file.file.name))
        return format_html('<br>'.join(file_links))
    get_files.short_description = 'Files'

    def approve_donation_requests(self, request, queryset):
        Post.objects.filter(id__in=queryset.values_list('post_id', flat=True)).update(is_approved=True)
    approve_donation_requests.short_description = "Approve selected donation requests"

    def deny_donation_requests(self, request, queryset):
        Post.objects.filter(id__in=queryset.values_list('post_id', flat=True)).update(is_approved=False)
    deny_donation_requests.short_description = "Deny selected donation requests"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'get_author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'author_name')

    def get_author(self, obj):
        if obj.author:
            return obj.author.username
        return obj.author_name or 'Unknown'
    get_author.short_description = 'Author'