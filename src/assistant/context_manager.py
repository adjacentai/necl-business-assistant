from collections import deque
from typing import List, Dict, Deque

class ContextManager:
    """
    Manages the conversation history for each user.
    Stores the last N messages in memory.
    """
    def __init__(self, max_history_size: int = 10):
        # Using a dictionary to hold a deque for each user's chat history.
        # A deque is efficient for appending and popping from both ends.
        self.history: Dict[int, Deque[Dict[str, str]]] = {}
        self.max_history_size = max_history_size

    def add_message(self, user_id: int, role: str, content: str):
        """
        Adds a new message to the user's history and ensures the history
        does not exceed the maximum size.

        Args:
            user_id: The ID of the user.
            role: The role of the message sender ('user' or 'assistant').
            content: The text content of the message.
        """
        if user_id not in self.history:
            self.history[user_id] = deque(maxlen=self.max_history_size)
        
        message = {"role": role, "content": content}
        self.history[user_id].append(message)

    def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """
        Retrieves the conversation history for a given user.

        Args:
            user_id: The ID of the user.

        Returns:
            A list of message dictionaries ready to be sent to the OpenAI API.
            Returns an empty list if the user has no history.
        """
        return list(self.history.get(user_id, []))

# Global instance of the context manager to be used across the application.
context_manager = ContextManager() 