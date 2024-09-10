from django.shortcuts import render, redirect
from django.contrib import messages
from posts.models import Post
from posts.forms import RegularPostForm
from posts.ai_moderation import perform_moderation
from posts.image_moderation import moderate_image
import logging

logger = logging.getLogger(__name__)

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
            
            moderation_result = perform_moderation(post.title, post.content)
            if moderation_result:
                messages.error(request, f"Text moderation failed: {moderation_result}")
                return redirect('home')

            post.is_approved = True  # Default to approved

            if 'image' in request.FILES:
                try:
                    logger.info("Starting image moderation")
                    image_moderation_result = moderate_image(request.FILES['image'])
                    logger.info(f"Image moderation result: {image_moderation_result}")
                    
                    if not image_moderation_result['is_safe']:
                        post.is_approved = False
                        messages.error(request, "The uploaded image contains inappropriate content and cannot be posted.")
                        logger.warning(f"Unsafe image detected. Inappropriate content: {image_moderation_result['inappropriate_percentage']:.2f}%")
                    else:
                        logger.info(f"Image approved. Inappropriate content: {image_moderation_result['inappropriate_percentage']:.2f}%")
                except Exception as e:
                    logger.error(f"Error processing image: {str(e)}", exc_info=True)
                    post.is_approved = False
                    messages.warning(request, "We couldn't process your image. Your post will be reviewed manually.")

            post.save()
            if post.is_approved:
                messages.success(request, 'Your post has been submitted successfully.')
            else:
                messages.info(request, 'Your post has been submitted for review.')
            return redirect('home')
        else:
            messages.error(request, 'There was an error with your post. Please check the form and try again.')
    else:
        form = RegularPostForm()

    context = {
        'form': form,
        'recent_posts': Post.objects.filter(is_approved=True).order_by('-created_at')[:5],
        'most_shared_posts': Post.objects.filter(is_approved=True).order_by('-share_count')[:5],
        'user': request.user,
    }
    return render(request, 'home.html', context)