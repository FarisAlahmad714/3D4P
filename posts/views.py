from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, DonationRequest, Comment
from .forms import RegularPostForm, DonationRequestForm, CommentForm, DonationRequestImageFormSet, DonationRequestFileFormSet
from .ai_moderation import perform_moderation
from .image_moderation import moderate_image
import logging
from django.views.generic import DetailView
from django.views.decorators.http import require_POST
from django.http import JsonResponse

logger = logging.getLogger(__name__)

@login_required
def select_post_type(request):
    return render(request, 'posts/select_post_type.html')


def create_regular_post(request):
    if request.method == 'POST':
        form = RegularPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.post_type = 'regular'

            # Text moderation - temporarily disabled for humanitarian content
            # moderation_result = perform_moderation(post.title, post.content)
            # if moderation_result:
            #     clear_messages(request)
            #     messages.error(request, f"Text moderation failed: {moderation_result}")
            #     return render(request, 'posts/create_regular_post.html', {'form': form})

            # Image moderation
            if 'image' in request.FILES:
                try:
                    logger.info("Starting image moderation")
                    image_moderation_result = moderate_image(request.FILES['image'])
                    logger.info(f"Image moderation result: {image_moderation_result}")
                    
                    if not image_moderation_result['is_safe']:
                        clear_messages(request)
                        messages.error(request, "The uploaded image contains inappropriate content and cannot be posted.")
                        logger.warning(f"Unsafe image detected. Inappropriate content: {image_moderation_result['inappropriate_percentage']:.2f}%")
                        return render(request, 'posts/create_regular_post.html', {'form': form})
                    else:
                        logger.info(f"Image approved. Inappropriate content: {image_moderation_result['inappropriate_percentage']:.2f}%")
                except Exception as e:
                    logger.error(f"Error processing image: {str(e)}", exc_info=True)
                    clear_messages(request)
                    messages.warning(request, "We couldn't process your image. Your post will be reviewed manually.")
                    post.is_approved = False
            
            post.is_approved = True
            post.save()
            messages.success(request, 'Your post has been created successfully.')
            return redirect('post_list')
        else:
            clear_messages(request)
            messages.error(request, 'There was an error with your post. Please check the form and try again.')
    else:
        form = RegularPostForm()

    return render(request, 'posts/create_regular_post.html', {'form': form})


@login_required
def create_donation_request(request):
    if request.method == 'POST':
        form = DonationRequestForm(request.POST, request.FILES)
        image_formset = DonationRequestImageFormSet(request.POST, request.FILES)
        file_formset = DonationRequestFileFormSet(request.POST, request.FILES)
        if form.is_valid() and image_formset.is_valid() and file_formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.post_type = 'donation'
            post.is_approved = False

            # Call the moderation function once - temporarily disabled for humanitarian content
            # moderation_result = perform_moderation(post.title, post.content)
            # if moderation_result:
            #     clear_messages(request)
            #     messages.error(request, f"Moderation failed: {moderation_result}")
            #     return render(request, 'posts/create_donation_request.html', {
            #         'form': form,
            #         'image_formset': image_formset,
            #         'file_formset': file_formset
            #     })
            
            post.save()
            messages.success(request, 'Your donation request has been created successfully.')
            return redirect('post_list')
        else:
            clear_messages(request)
            messages.error(request, 'There was an error with your donation request. Please check the form and try again.')
    else:
        form = DonationRequestForm()
        image_formset = DonationRequestImageFormSet()
        file_formset = DonationRequestFileFormSet()

    return render(request, 'posts/create_donation_request.html', {
        'form': form,
        'image_formset': image_formset,
        'file_formset': file_formset
    })


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        post.delete()
        clear_messages(request)
        messages.success(request, 'Your post has been deleted successfully.')
    else:
        clear_messages(request)
        messages.error(request, 'You do not have permission to delete this post.')
    return redirect('user_profile', username=request.user.username)


def post_list(request):
    posts = Post.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'posts/post_list.html', {'posts': posts})

def donation_list(request):
    donation_posts = Post.objects.filter(post_type='donation', is_approved=True).order_by('-created_at')
    return render(request, 'posts/donation_list.html', {'posts': donation_posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.view_count += 1
    post.save()

    # Create donation goal for donation posts if it doesn't exist
    if post.post_type == 'donation':
        from donations.models import DonationGoal
        from decimal import Decimal
        
        if not hasattr(post, 'donation_goal'):
            # Use the estimated cost from donation details if available
            default_goal = Decimal('5000.00')  # Default goal
            if hasattr(post, 'donation_details') and post.donation_details:
                default_goal = post.donation_details.estimated_cost
            
            DonationGoal.objects.create(
                post=post,
                goal_amount=default_goal,
                is_active=True
            )
        else:
            # Update current amount
            post.donation_goal.update_current_amount()

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


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_object(self):
        obj = super().get_object()
        if not self.request.session.get(f'post_{obj.id}_viewed'):
            obj.increment_view_count()
            self.request.session[f'post_{obj.id}_viewed'] = True
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_shared'] = self.request.GET.get('shared') == 'true'
        return context


@require_POST
def share_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.increment_share_count()
    return JsonResponse({'success': True, 'share_count': post.share_count})


# Helper function to clear messages
def clear_messages(request):
    storage = messages.get_messages(request)
    storage.used = True
