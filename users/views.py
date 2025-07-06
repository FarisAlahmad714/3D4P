from django.shortcuts import render, redirect , get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .forms import CustomUserCreationForm, MemberVerificationImageFormSet
from .models import MemberApplication, MemberVerificationImage
from .decorators import verified_member_required
from .forms import MemberProfileForm
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import MemberProfile
from posts.models import Post
import logging
from django.db import connection
from django.contrib.auth.models import User
from django.http import Http404
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disclaimer'] = """
        Please note that member signup is specifically for individuals seeking to make donation requests for prosthetic needs. 
        If you're looking to donate, you don't need to sign up - we only require your email address when proceeding to the donation page.
        """
        return context
    
    def form_valid(self, form):
        if self.request.POST.get('disclaimer_agreed') != 'true':
            form.add_error(None, 'You must acknowledge the disclaimer before signing up.')
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        user = form.save()
        
        # Handle multiple file uploads
        files = self.request.FILES.getlist('verification_files')
        if files:
            # Use first file as proof_image for MemberApplication
            member_application = MemberApplication.objects.create(user=user, proof_image=files[0])
            
            # Save all files as verification images
            for file in files:
                MemberVerificationImage.objects.create(
                    application=member_application,
                    image=file
                )
        
        messages.success(self.request, 'Your account has been created successfully. You can now log in.')
        return response
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}" if field != '__all__' else error)
        return self.render_to_response(self.get_context_data(form=form))
    
class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()
        MemberProfile.objects.get_or_create(user=user)
        return response

@login_required
def profile(request):
    return render(request, 'users/profile.html')

def custom_logout(request):
    logout(request)
    return redirect('home')

@login_required
def application_status(request):
    return render(request, 'users/application_status.html')

@verified_member_required
def member_only_view(request):
    return render(request, 'members.html')
    

def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('home')

User = get_user_model()

def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user, is_approved=True)

    if request.user.is_authenticated and request.user == profile_user:
        if request.method == 'POST':
            u_form = UserUpdateForm(request.POST, instance=profile_user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_user.memberprofile)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('user_profile', username=username)
        else:
            u_form = UserUpdateForm(instance=profile_user)
            p_form = ProfileUpdateForm(instance=profile_user.memberprofile)
    else:
        u_form = None
        p_form = None

    context = {
        'profile_user': profile_user,
        'posts': posts,
        'u_form': u_form,
        'p_form': p_form,
        'is_own_profile': request.user.is_authenticated and request.user == profile_user
    }

    return render(request, 'users/profile.html', context)