
import requests
import re
import os
import json

# Your OpenRouter API key.
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

def clean_text(text):
    """Remove '**' and special symbols; keep alphanumerics, whitespace, and basic punctuation."""
    text = text.replace("**", "")
    text = re.sub(r'[^\w\s.,?!]', '', text)
    return text

def generate_answer(question, max_length=1000, emotion=None):
    """Generate answer via OpenRouter API."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "API Key not configured. Please add OPENROUTER_API_KEY."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = "You are a helpful AI tutor for XPRESSAI. Keep answers concise, direct, and conversational."
    if emotion:
        system_prompt += f" The user is currently feeling {emotion}."

    data = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    }

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=15
        )
        response.raise_for_status()
        result = response.json()
        text = result["choices"][0]["message"]["content"]
        
        words = text.split()
        if len(words) > max_length:
            text = ' '.join(words[:max_length])
        return text
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"