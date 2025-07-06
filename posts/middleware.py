from .models import Post

class PostViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/post/') and request.method == 'GET':
            post_id = request.path.split('/')[-2]
            try:
                post = Post.objects.get(pk=post_id)
                session_key = 'viewed_post_{}'.format(post_id)
                if not request.session.get(session_key, False):
                    post.view_count += 1
                    post.save()
                    request.session[session_key] = True
            except Post.DoesNotExist:
                pass
        return response