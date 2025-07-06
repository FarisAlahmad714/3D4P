from django.shortcuts import render
from posts.models import Post

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
            'question': 'How do I request prosthetic assistance?',
            'answer': 'Create an account, verify your identity by providing required documentation, then submit a detailed request explaining your needs and circumstances.'
        },
        {
            'question': 'Is there a fee to use this platform?',
            'answer': 'No, our platform is completely free for both those requesting assistance and donors. We believe prosthetic help should be accessible to everyone.'
        },
        {
            'question': 'How are requests verified?',
            'answer': 'Our team reviews all requests and supporting documentation to ensure legitimacy. This process typically takes 24-48 hours.'
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