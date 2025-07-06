"""
Language utilities for 3D4P multilingual support
"""
from django.conf import settings
from django.utils import translation
from django.utils.translation import get_language_info

def get_language_direction(language_code=None):
    """
    Return the text direction for a language code.
    Returns 'rtl' for right-to-left languages, 'ltr' for left-to-right.
    """
    if language_code is None:
        language_code = translation.get_language()
    
    rtl_languages = getattr(settings, 'RTL_LANGUAGES', ['ar', 'he', 'fa', 'ur'])
    return 'rtl' if language_code in rtl_languages else 'ltr'

def get_language_font_family(language_code=None):
    """
    Return appropriate font family for a language code.
    """
    if language_code is None:
        language_code = translation.get_language()
    
    font_families = {
        'ar': "'Noto Sans Arabic', 'Amiri', Arial, sans-serif",
        'he': "'Noto Sans Hebrew', Arial, sans-serif", 
        'fa': "'Noto Sans Devanagari', Arial, sans-serif",
        'ur': "'Noto Sans Arabic', Arial, sans-serif",
        'zh': "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        'ja': "'Noto Sans JP', 'Yu Gothic', sans-serif",
        'ko': "'Noto Sans KR', 'Malgun Gothic', sans-serif",
        'hi': "'Noto Sans Devanagari', Arial, sans-serif",
        'th': "'Noto Sans Thai', Arial, sans-serif",
    }
    
    return font_families.get(language_code, "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif")

def get_available_languages():
    """
    Return list of available languages with additional info.
    """
    languages = []
    for code, name in settings.LANGUAGES:
        try:
            lang_info = get_language_info(code)
            languages.append({
                'code': code,
                'name': name,
                'name_local': lang_info.get('name_local', name),
                'bidi': lang_info.get('bidi', False),
                'direction': get_language_direction(code),
                'font_family': get_language_font_family(code),
            })
        except:
            languages.append({
                'code': code,
                'name': name,
                'name_local': name,
                'bidi': code in getattr(settings, 'RTL_LANGUAGES', []),
                'direction': get_language_direction(code),
                'font_family': get_language_font_family(code),
            })
    
    return languages