"""
Template tags for simple translation system
"""
from django import template
from django.utils.safestring import mark_safe
from .simple_translation import get_translation, get_language_info

register = template.Library()

@register.simple_tag(takes_context=True)
def translate(context, text):
    """
    Simple translation tag that uses session language
    """
    request = context.get('request')
    if request:
        language = request.session.get('language', 'en')
    else:
        language = 'en'
    
    return get_translation(text, language)

@register.simple_tag(takes_context=True)
def get_current_language_info(context):
    """
    Get current language info from session
    """
    request = context.get('request')
    if request:
        language = request.session.get('language', 'en')
    else:
        language = 'en'
    
    return get_language_info(language)