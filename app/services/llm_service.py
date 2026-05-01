import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize the Groq client
# This expects the GROQ_API_KEY environment variable to be set.
client = Groq()

def call_llm(prompt: str) -> str:
    """
    Calls the Groq LLM using the chat completions API.
    Returns the deterministic, raw text response.
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a highly precise data extraction assistant. You only output valid JSON. No markdown formatting like ```json, no explanations, no prefix or suffix."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-70b-8192",
            temperature=0.0,  # Deterministic response
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "{}"
