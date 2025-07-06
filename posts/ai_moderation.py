from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def check_for_donation_request(content):
    prompt = f"""Analyze the following text and determine if it contains an active request for donations or financial assistance. 
    Respond with 'Yes' only if the text explicitly asks for money or donations. 
    Respond with 'No' if the text merely mentions past donations or expresses gratitude for previous support.
    
    Text to analyze: {content}
    
    Respond with only 'Yes' or 'No'."""
    
    try:
        response = client.chat.completions.create(
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
    You are moderating content for a MEDICAL PROSTHETIC DONATION PLATFORM that helps injured people get prosthetic limbs.

    ONLY flag content that contains:
    - Explicit sexual content
    - Personal private information (addresses, phone numbers)
    - Clear spam or commercial advertising

    DO NOT flag content that mentions:
    - Any military, army, or conflict (this is a medical platform for war injuries)
    - Any country, city, or geographic location
    - Medical terms like "blast injury", "amputation", "lost limb"
    - ANY humanitarian or medical need

    This platform specifically helps people injured in conflicts get prosthetic limbs. Political references are part of explaining medical needs.

    If the content is requesting prosthetic help or describing medical needs, respond ONLY with: "Post is clean."

    Title: {title}
    Content: {content}
    """

    donation_prompt = f"""This is a HUMANITARIAN PROSTHETIC DONATION PLATFORM. Analyze if this content contains inappropriate donation requests (spam, scams, non-medical requests).

    APPROPRIATE requests include:
    - Prosthetic limbs or medical devices
    - Medical treatments related to amputations
    - Humanitarian aid for injured individuals
    - Legitimate medical fundraising

    INAPPROPRIATE requests include:
    - General money requests unrelated to prosthetics
    - Commercial sales or business promotion
    - Spam or scam content

    Respond 'Yes' only if the request is INAPPROPRIATE for a medical prosthetic platform.
    Respond 'No' if it's appropriate medical/humanitarian content.
    
    Title: {title}
    Content: {content}
    
    Respond with only 'Yes' or 'No'."""

    try:
        moderation_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI trained to moderate post content for inappropriate or offensive material."},
                {"role": "user", "content": moderation_prompt}
            ]
        )
        moderation_result = moderation_response.choices[0].message.content.strip()
        print(f"AI moderation result: {moderation_result}")

        donation_response = client.chat.completions.create(
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