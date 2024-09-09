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
        print(f"AI detection result: {result}")
        return result
    except Exception as e:
        print(f"Error in AI detection: {str(e)}")
        return False
    

def keyword_check(content):
    keywords = ['donate', 'donation', 'financial assistance', 'money needed', 'fund me', 'need funds']
    content_lower = content.lower()
    return any(keyword in content_lower for keyword in keywords)   