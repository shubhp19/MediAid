import base64
import mimetypes
import requests
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def encode_image(image_path):
    """
    Encode an image file to base64 format.
    """
    try:
        with open(image_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode("utf-8")
        return encoded_string
    except Exception as e:
        logger.error(f"[ERROR] Failed to encode image: {e}")
        return None

def analyze_image_with_query(query, model, encoded_image=None, image_filepath=None):
    """
    Send a request to the Groq API to analyze the image and respond to the query.
    Requires a valid encoded_image or image_filepath for determining MIME type.
    """
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found in environment variables.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    mime_type = "image/jpeg"  # default
    if image_filepath:
        mime_type, _ = mimetypes.guess_type(image_filepath)
        if not mime_type:
            mime_type = "image/jpeg"
        logger.debug(f"Detected MIME type: {mime_type} for file: {image_filepath}")

    # If we have an encoded image, embed it into the prompt
    if encoded_image:
        image_url = f"data:{mime_type};base64,{encoded_image}"
    elif image_filepath:
        encoded_image = encode_image(image_filepath)
        if encoded_image:
            image_url = f"data:{mime_type};base64,{encoded_image}"
        else:
            logger.error("Failed to encode image from filepath.")
            return "Failed to process the uploaded image."
    else:
        image_url = None

    messages = [
        {"role": "system", "content": "You are a helpful medical assistant AI. Provide clear and concise answers."},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": query}
            ] if not image_url else [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": query}
            ]
        }
    ]

    url = "https://api.groq.com/openai/v1/chat/completions"  # Correct endpoint for vision tasks

    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 1024
    }

    try:
        logger.debug(f"Sending request to {url} with body: {body}")
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Response received: {result}")
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        logger.error(f"[ERROR] Request failed: {e}")
        return f"Failed to get response from the AI server: {str(e)}. Please check your internet connection or API key."
    except KeyError as e:
        logger.error(f"[ERROR] Unexpected response format: {e}")
        return "Invalid response from the AI model."
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error: {e}")
        return "An unexpected error occurred while processing your request."