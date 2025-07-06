from django import template

register = template.Library()

@register.filter
def is_member(user):
    if user is None or not user.is_authenticated:
        return False
    return hasattr(user, 'memberprofile') and user.memberprofile.is_verified