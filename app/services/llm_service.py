import os
import re
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize the Groq client
client = Groq()

def clean_llm_output(response: str) -> str:
    """
    Cleans raw LLM output before JSON parsing.
    Removes code block markers and all invalid control characters.
    """
    response = response.strip()
    # Remove code block markers
    response = re.sub(r"```json|```", "", response)
    # Remove ALL control characters (0x00–0x1F and 0x7F)
    # This is aggressive but ensures json.loads never hits a control char error
    response = re.sub(r"[\x00-\x1F\x7F]", " ", response)
    return response.strip()

def safe_parse(response: str):
    """
    Attempts to parse the response as JSON with a fallback.
    """
    import json
    try:
        return json.loads(response)
    except Exception:
        # Attempt fixing single quotes used instead of double quotes
        fixed = response.replace("'", '"')
        try:
            return json.loads(fixed)
        except Exception:
            return {}

def call_llm(prompt: str) -> str:
    """
    Calls the Groq LLM using the chat completions API.
    Cleans and returns the raw text response.
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a highly precise data extraction assistant. "
                        "You ONLY output valid, directly parsable JSON. "
                        "Do NOT include: explanations, markdown formatting, "
                        "code blocks, newlines inside string values, or comments. "
                        "Ensure output is directly parsable by json.loads()."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.0,
        )
        raw = response.choices[0].message.content
        print("RAW LLM OUTPUT:\n", raw[:500])  # Debug: print first 500 chars
        cleaned = clean_llm_output(raw)
        return cleaned
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "{}"
