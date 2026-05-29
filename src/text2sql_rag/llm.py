#!/usr/bin/env python3
"""
LLM Integration Module
Professional implementation for calling various LLM APIs
"""

import os
import requests
import json
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def call_llm(model: str, prompt: str) -> str:
    """Call specified LLM with the given prompt"""
    if model.lower() == 'typhoon':
        return call_typhoon(prompt)
    elif model.lower() in ['openai', 'gpt']:
        return call_openai(prompt)
    elif model.lower() == 'claude':
        return call_claude(prompt)
    elif model.lower() == 'gemini':
        return call_gemini(prompt)
    else:
        raise ValueError(f"Unsupported model: {model}")

def call_typhoon(prompt: str) -> str:
    """Call Typhoon API"""
    TYPHOON_ENDPOINT = "https://api.opentyphoon.ai/v1/chat/completions"
    TYPHOON_API_KEY = os.getenv("TYPHOON_API_KEY")
    
    if not TYPHOON_API_KEY:
        raise ValueError("TYPHOON_API_KEY not found in environment variables")
    
    headers = {
        "Authorization": f"Bearer {TYPHOON_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "typhoon-v2.1-12b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.0
    }
    
    try:
        response = requests.post(TYPHOON_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Typhoon API error: {e}")
    except KeyError as e:
        raise Exception(f"Unexpected Typhoon API response format: {e}")

def call_openai(prompt: str) -> str:
    """Call OpenAI API"""
    try:
        import openai
        
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.0
        )
        
        return response.choices[0].message.content
        
    except ImportError:
        raise Exception("OpenAI library not installed. Install with: pip install openai")
    except Exception as e:
        raise Exception(f"OpenAI API error: {e}")

def call_claude(prompt: str) -> str:
    """Call Anthropic Claude API"""
    try:
        import anthropic
        
        ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
        
    except ImportError:
        raise Exception("Anthropic library not installed. Install with: pip install anthropic")
    except Exception as e:
        raise Exception(f"Claude API error: {e}")

def call_gemini(prompt: str) -> str:
    """Call Google Gemini API"""
    try:
        import google.generativeai as genai
        
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=2000,
                temperature=0.0
            )
        )
        
        return response.text
        
    except ImportError:
        raise Exception("Google GenerativeAI library not installed. Install with: pip install google-generativeai")
    except Exception as e:
        raise Exception(f"Gemini API error: {e}")

def extract_sql(response: str) -> str:
    """Extract SQL from LLM response"""
    if not response:
        return ""
    
    # Look for SQL code blocks
    sql_patterns = [
        r'```sql\n?(.*?)\n?```',
        r'```\n?(.*?)\n?```',
        r'SELECT.*?;',
        r'SELECT.*?(?=\n|$)'
    ]
    
    for pattern in sql_patterns:
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        if matches:
            sql = matches[0].strip()
            # Keep semicolon at the end
            return sql
    
    # If no pattern matches, return the response as-is
    return response.strip()
