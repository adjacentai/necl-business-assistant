from typing import List, Dict, Any, Optional

# --- System Prompt ---
# This defines the persona and instructions for the AI assistant.
SYSTEM_PROMPT = """
You are a friendly and helpful AI assistant for a flower shop.
Your goal is to assist customers with their orders, provide information about flowers, and handle common inquiries.
Be polite, concise, and always stay in character.
You should not answer questions that are not related to flowers, the shop, or customer orders.
"""

def build_prompt(history: List[Dict[str, str]], user_text: str) -> List[Dict[str, str]]:
    """
    Builds a list of messages for the OpenAI API call.

    :param history: The conversation history.
    :param user_text: The user's current message.
    :return: A list of messages formatted for the API.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)

    # Here, we can customize the user's message.
    # For now, we'll just use the raw text.
    formatted_user_message = {"role": "user", "content": user_text}

    messages.append(formatted_user_message)
    return messages
