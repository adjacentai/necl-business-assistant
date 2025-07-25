import logging
import json
from typing import List, Dict, Optional, Any

from openai import AsyncOpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL_NAME
from src.assistant.prompts import NLU_SYSTEM_PROMPT

# Initialize the asynchronous OpenAI client
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def get_openai_response(messages: List[Dict[str, str]]) -> Optional[str]:
    """
    Sends a request to the OpenAI API to get a chat completion.

    Args:
        messages: A list of message dictionaries, following the OpenAI API format.
                  Example: [{"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": "Hello!"}]

    Returns:
        The content of the assistant's response message as a string, or None if an error occurs.
    """
    if not messages:
        logging.warning("get_openai_response called with empty messages list.")
        return None

    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=messages
        )
        # Accessing the response content correctly
        if response.choices and response.choices[0].message:
            return response.choices[0].message.content
        else:
            logging.error("OpenAI response is empty or invalid.")
            return None
    except Exception as e:
        logging.error(f"An error occurred while communicating with OpenAI: {e}")
        return None


async def get_intent_from_openai(user_text: str) -> Optional[Dict[str, Any]]:
    """
    Identifies the user's intent by calling the OpenAI API with a specialized NLU prompt.

    Args:
        user_text: The raw text from the user's message.

    Returns:
        A dictionary containing the 'intent' and 'entities', or None if it fails.
    """
    messages = [
        {"role": "system", "content": NLU_SYSTEM_PROMPT},
        {"role": "user", "content": user_text}
    ]

    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0
        )

        if response.choices and response.choices[0].message:
            response_text = response.choices[0].message.content
            intent_data = json.loads(response_text)
            return intent_data
        else:
            logging.error("NLU response from OpenAI is empty or invalid.")
            return None
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON from NLU response: {e}")
        return None
    except Exception as e:
        logging.error(f"An error occurred during NLU processing: {e}")
        return None
