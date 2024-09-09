from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, DonationRequest , Comment
from .forms import RegularPostForm, DonationRequestForm ,CommentForm
from .ai_moderation import check_for_donation_request, keyword_check

@login_required
def select_post_type(request):
    return render(request, 'posts/select_post_type.html')

def create_regular_post(request):
    if request.method == 'POST':
        form = RegularPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            if request.user.is_authenticated:
                post.author = request.user
            else:
                post.author_name = form.cleaned_data['author_name']
            post.post_type = 'regular'
            
            ai_result = check_for_donation_request(post.content)
            keyword_result = keyword_check(post.content)
            
            if ai_result and keyword_result:
                messages.error(request, 'Your post appears to contain a request for financial assistance. This is not allowed in regular posts. Please use the donation request form for such posts.')
                return render(request, 'posts/create_post.html', {'form': form})
            elif ai_result or keyword_result:
                post.is_approved = False
                post.save()
                messages.warning(request, 'Your post may contain content related to donations. It has been submitted for review.')
                return redirect('post_list')
            else:
                post.is_approved = True
                post.save()
                messages.success(request, 'Your post has been created successfully.')
                return redirect('post_list')
        else:
            messages.error(request, 'There was an error with your post. Please check the form and try again.')
    else:
        form = RegularPostForm()
    
    return render(request, 'posts/create_regular_post.html', {'form': form})
    
@login_required
def create_donation_request(request):
    if request.method == 'POST':
        form = DonationRequestForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.post_type = 'donation'
            post.is_approved = False
            post.save()
            messages.success(request, 'Your donation request has been submitted for review.')
            return redirect('post_list')
    else:
        form = DonationRequestForm()
    
    return render(request, 'posts/create_donation_request.html', {'form': form})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Your post has been deleted.')
        return redirect('profile')
    return render(request, 'posts/confirm_delete.html', {'post': post})

def post_list(request):
    posts = Post.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'posts/post_list.html', {'posts': posts})

def post_detail(request, pk,post_id):
    post = get_object_or_404(Post, id=post_id)
    post.view_count += 1
    post.save()
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            if request.user.is_authenticated:
                comment.author = request.user
            else:
                comment.author_name = form.cleaned_data['author_name']
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'posts/post_detail.html', {'post': post, 'comments': comments, 'form': form})