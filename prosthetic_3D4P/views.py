from django.shortcuts import render, redirect
from django.contrib import messages
from posts.models import Post
from posts.forms import RegularPostForm
from posts.ai_moderation import check_for_donation_request, keyword_check

def home(request):
    if request.method == 'POST':
        form = RegularPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            if request.user.is_authenticated:
                post.author = request.user
            else:
                post.author_name = form.cleaned_data.get('author_name')
            
            post.post_type = 'regular'
            
            ai_result = check_for_donation_request(post.content)
            keyword_result = keyword_check(post.content)
            
            if ai_result and keyword_result:
                messages.error(request, 'Your post appears to contain a request for financial assistance. This is not allowed in regular posts.')
            elif ai_result or keyword_result:
                post.is_approved = False
                post.save()
                messages.warning(request, 'Your post may contain content related to donations. It has been submitted for review.')
            else:
                post.is_approved = True
                post.save()
                messages.success(request, 'Your post has been created successfully.')
            return redirect('home')
        else:
            messages.error(request, 'There was an error with your post. Please check the form and try again.')
    else:
        form = RegularPostForm()
    
    context = {
        'form': form,
        'recent_posts': Post.objects.filter(is_approved=True).order_by('-created_at')[:5],
        'most_shared_posts': Post.objects.filter(is_approved=True).order_by('-share_count')[:5],
        'user': request.user,  # Explicitly add the user to the context
    }
    return render(request, 'home.html', context)