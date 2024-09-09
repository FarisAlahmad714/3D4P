from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser, MemberApplication

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