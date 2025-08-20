from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from posts.models import Post
import os

def home(request):
    recent_posts = Post.objects.filter(is_approved=True).order_by('-created_at')[:5]
    most_shared_posts = Post.objects.filter(is_approved=True).order_by('-share_count')[:5]
    
    context = {
        'recent_posts': recent_posts,
        'most_shared_posts': most_shared_posts,
    }
    return render(request, 'home.html', context)


def how_it_works(request):
    """View for How It Works support page"""
    return render(request, 'support/how_it_works.html')


def faq(request):
    """View for FAQ support page"""
    faqs = [
        {
            'question': 'What verification is required to receive donations?',
            'answer': 'All users must complete rigorous verification including: extensive medical documentation proving prosthetic need, government-issued ID (passport or national ID), and manual review by our verification team. For users under 16, parent/guardian documentation is also required.'
        },
        {
            'question': 'How long does the verification process take?',
            'answer': 'Our verification team typically completes the review process within 24-48 hours. Complex cases may take longer. You will be notified via email once verification is complete.'
        },
        {
            'question': 'What medical documentation is required?',
            'answer': 'You must provide complete medical history, official diagnosis from certified healthcare providers, proof of prosthetic need, and any relevant medical reports or recommendations from doctors.'
        },
        {
            'question': 'Can I submit a request before verification?',
            'answer': 'Yes, you can submit your donation request, but it will not be published until verification is complete. This ensures all public requests are from verified, legitimate recipients.'
        },
        {
            'question': 'What happens if my verification is rejected?',
            'answer': 'If verification cannot be completed, we will contact you with specific reasons and guidance on how to provide additional documentation if possible.'
        },
        {
            'question': 'How do I request prosthetic assistance?',
            'answer': 'Create an account, submit your donation request with all required documentation, complete the verification process, then your verified request will be published for donors to support.'
        },
        {
            'question': 'Is there a fee to use this platform?',
            'answer': 'No, our platform is completely free for both those requesting assistance and donors. We believe prosthetic help should be accessible to everyone.'
        },
        {
            'question': 'How are requests verified?',
            'answer': 'Our trained verification specialists manually review all medical documentation, government ID, and request details to ensure legitimacy and prevent fraud.'
        },
        {
            'question': 'What types of prosthetics are covered?',
            'answer': 'We support requests for all types of prosthetic devices including limbs, hearing aids, and other assistive devices.'
        },
        {
            'question': 'How do donations work?',
            'answer': 'Donors can contribute directly to specific requests or to our general fund. All donations are processed securely and go directly to prosthetic costs.'
        },
        {
            'question': 'What if my request is not fully funded?',
            'answer': 'Partially funded requests remain active, and we actively promote them to potential donors. You can also share your request on social media.'
        },
        {
            'question': 'Can I update my request after submitting?',
            'answer': 'Yes, you can edit your request details, add photos, or provide updates on your situation through your account dashboard.'
        },
        {
            'question': 'How do I track my request progress?',
            'answer': 'Your dashboard shows real-time funding progress, donor messages, and any updates from our team.'
        }
    ]
    
    context = {'faqs': faqs}
    return render(request, 'support/faq.html', context)


def contact_us(request):
    """View for Contact Us support page"""
    return render(request, 'support/contact_us.html')


def privacy_policy(request):
    """View for Privacy Policy support page"""
    return render(request, 'support/privacy_policy.html')


def debug_media(request):
    """Debug view to check media configuration"""
    debug_info = []
    
    debug_info.append(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    debug_info.append(f"MEDIA_URL: {settings.MEDIA_URL}")
    debug_info.append(f"MEDIA_ROOT exists: {os.path.exists(settings.MEDIA_ROOT)}")
    
    if os.path.exists(settings.MEDIA_ROOT):
        try:
            contents = os.listdir(settings.MEDIA_ROOT)
            debug_info.append(f"MEDIA_ROOT contents: {contents}")
            
            post_images_path = os.path.join(settings.MEDIA_ROOT, 'post_images')
            if os.path.exists(post_images_path):
                post_images = os.listdir(post_images_path)
                debug_info.append(f"post_images contents: {post_images}")
                
                # Check specific file from error
                test_file = os.path.join(post_images_path, 'photo_2025-07-30_17-46-47_GtUDQfh.jpg')
                debug_info.append(f"Test file exists: {os.path.exists(test_file)}")
                if os.path.exists(test_file):
                    stat = os.stat(test_file)
                    debug_info.append(f"Test file size: {stat.st_size} bytes")
                    debug_info.append(f"Test file permissions: {oct(stat.st_mode)}")
            else:
                debug_info.append("post_images directory does not exist")
        except Exception as e:
            debug_info.append(f"Error listing directory: {e}")
    
    # Test write permissions
    try:
        test_file = os.path.join(settings.MEDIA_ROOT, 'test_write.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        debug_info.append("Write permissions: OK")
    except Exception as e:
        debug_info.append(f"Write permissions: FAILED - {e}")
    
    return HttpResponse('<br>'.join(debug_info))


def firebase_test(request):
    """View for Firebase integration test page"""
    return render(request, 'firebase_test.html')