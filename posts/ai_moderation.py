import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY


def check_for_donation_request(content):
    prompt = f"""Analyze the following text and determine if it contains an active request for donations or financial assistance. 
    Respond with 'Yes' only if the text explicitly asks for money or donations. 
    Respond with 'No' if the text merely mentions past donations or expresses gratitude for previous support.
    
    Text to analyze: {content}
    
    Respond with only 'Yes' or 'No'."""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI trained to detect explicit requests for donations or financial assistance."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content.strip().lower() == 'yes'
        print(f"AI donation request detection result: {result}")
        return result
    except Exception as e:
        print(f"Error in AI donation request detection: {str(e)}")
        return False


def keyword_check(content):
    keywords = ['donate', 'donation', 'financial assistance', 'money needed', 'fund me', 'need funds']
    content_lower = content.lower()
    return any(keyword in content_lower for keyword in keywords)   


def perform_moderation(title, content):
    moderation_prompt = f"""
    Please analyze the following post title and content and identify if they contain any of the following:
    - Profanity or explicit language
    - Hate speech or discriminatory language
    - Personal information or sensitive data
    - Inappropriate or offensive content

    If any of the above are detected, please respond with the specific category and a brief explanation. If the title and content are clean and appropriate, simply respond with "Post is clean."

    Title: {title}
    Content: {content}
    """

    donation_prompt = f"""Analyze the following post title and content and determine if they contain an active request for donations or financial assistance. 
    Respond with 'Yes' only if the text explicitly asks for money or donations. 
    Respond with 'No' if the text merely mentions past donations or expresses gratitude for previous support.
    
    Title: {title}
    Content: {content}
    
    Respond with only 'Yes' or 'No'."""

    try:
        moderation_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI trained to moderate post content for inappropriate or offensive material."},
                {"role": "user", "content": moderation_prompt}
            ]
        )
        moderation_result = moderation_response.choices[0].message.content.strip()
        print(f"AI moderation result: {moderation_result}")

        donation_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI trained to detect explicit requests for donations or financial assistance."},
                {"role": "user", "content": donation_prompt}
            ]
        )
        donation_result = donation_response.choices[0].message.content.strip().lower() == 'yes'
        print(f"AI donation request detection result: {donation_result}")

        if moderation_result != "Post is clean.":
            return moderation_result
        elif donation_result:
            return "The post contains a request for donations or financial assistance."
        else:
            return None
    except Exception as e:
        print(f"Error in AI moderation: {str(e)}")
        return None