import aiohttp
import logging
from typing import Dict, Any, Optional

from src.config import RASA_API_URL

async def get_rasa_intent(user_id: str, text: str) -> Optional[Dict[str, Any]]:
    """
    Sends a message to the Rasa server to get the intent and entities.

    Args:
        user_id: The unique identifier for the user.
        text: The message from the user.

    Returns:
        A dictionary containing the top intent and entities, or None if an error occurs.
        Example: {'intent': 'greet', 'entities': [{'entity': 'name', 'value': 'John'}]}
    """
    payload = {
        "sender": user_id,
        "message": text
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(RASA_API_URL, json=payload) as response:
                if response.status == 200:
                    rasa_response = await response.json()
                    # Assuming the response is a list of tracker events,
                    # we are interested in the latest `user` message's parse data.
                    # A direct call to /model/parse returns the parse data directly.
                    # Since we are using the webhook, we might get a different structure.
                    # Let's assume a direct /model/parse structure for now for simplicity,
                    # as it's a common use case.
                    # If rasa_response is a list, it's from the webhook.
                    if isinstance(rasa_response, list) and rasa_response:
                        # Find the latest bot message with parse data
                        for event in reversed(rasa_response):
                            if event.get('event') == 'user':
                                return {
                                    'intent': event.get('parse_data', {}).get('intent', {}).get('name'),
                                    'entities': event.get('parse_data', {}).get('entities', [])
                                }
                    # If it's a direct response from /model/parse
                    elif isinstance(rasa_response, dict):
                         return {
                            'intent': rasa_response.get('intent', {}).get('name'),
                            'entities': rasa_response.get('entities', [])
                        }
                    return None
                else:
                    logging.error(f"Rasa server returned status {response.status}: {await response.text()}")
                    return None
    except aiohttp.ClientConnectorError as e:
        logging.error(f"Could not connect to Rasa server at {RASA_API_URL}. Error: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while communicating with Rasa: {e}")
        return None 