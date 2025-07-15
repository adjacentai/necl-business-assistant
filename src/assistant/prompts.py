from typing import List, Dict, Any, Optional

# --- System Prompt ---
# This defines the persona and instructions for the AI assistant.
SYSTEM_PROMPT = """
You are a friendly and helpful AI assistant for a flower shop.
Your goal is to assist customers with their orders, provide information about flowers, and handle common inquiries.
Be polite, concise, and always stay in character.
You should not answer questions that are not related to flowers, the shop, or customer orders.
"""

def build_prompt(history: List[Dict[str, str]], user_text: str, rasa_intent: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    """
    Constructs the full prompt to be sent to the OpenAI API.

    Args:
        history: A list of previous messages in the conversation.
        user_text: The latest raw text from the user.
        rasa_intent: The structured data (intent and entities) from Rasa.

    Returns:
        A list of message dictionaries formatted for the OpenAI API.
    """
    # Start with the system prompt that defines the bot's persona
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add the conversation history
    messages.extend(history)
    
    # Here, we can customize the user's message based on Rasa's output.
    # For now, we'll keep it simple and just use the user's raw text.
    # In a more advanced setup, you could use the intent and entities
    # to create a more structured and informative prompt.
    
    # Example of how you might use the intent:
    if rasa_intent and rasa_intent.get('intent'):
        intent = rasa_intent['intent']
        entities = rasa_intent.get('entities', [])
        
        # You could create a more specific prompt for the LLM
        # For example: "The user wants to 'order_flowers'. They mentioned: tulips."
        # For now, we will just pass the raw text to keep it simple.
        prompt_content = f"User message: '{user_text}' (Intent detected: {intent})"
        
    else:
        # If Rasa fails or doesn't return an intent, fall back to the raw text
        prompt_content = user_text

    # Add the current user message to the list
    messages.append({"role": "user", "content": prompt_content})
    
    return messages
