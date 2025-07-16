from aiogram import types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .routers import main_router
from src.assistant.logger import log_user_message, log_assistant_response
from src.assistant.context_manager import get_history, add_message
from src.assistant.openai_client import get_openai_response, get_intent_from_openai
from src.assistant.prompts import build_prompt
from src.bot.keyboards import create_main_menu_keyboard

# A simple in-memory storage for user processing status.
# Using a set for efficient add/remove operations.
processing_users = set()


@main_router.message(CommandStart())
async def handle_start(message: types.Message):
    """
    Handler for the /start command.
    Greets the user and logs the interaction.
    """
    user_id = message.from_user.id
    welcome_text = (
        "Здравствуйте! Я ваш AI-ассистент для цветочного магазина. "
        "Чем могу помочь?"
    )
    
    log_user_message(user_id, message.text)
    await message.answer(welcome_text)
    log_assistant_response(user_id, welcome_text)


@main_router.message()
async def handle_text_message(message: Message, state: FSMContext):
    """
    Handles incoming text messages from the user.
    Integrates OpenAI to provide an intelligent response.
    """
    user_id = message.from_user.id

    if user_id in processing_users:
        await message.answer("Пожалуйста, подождите, я обрабатываю ваш предыдущий запрос.")
        return

    processing_users.add(user_id)
    try:
        user_text = message.text
        log_user_message(user_id, user_text)
        
        # Add user message to context immediately
        add_message(user_id, 'user', user_text)

        if not user_text:
            return

        # 1. Get user's intent
        intent_data = await get_intent_from_openai(user_text)
        # Optional: Log the detected intent
        # logging.info(f"User {user_id} intent: {intent_data}")

        # 2. Get conversation history
        history = get_history(user_id)

        # 3. Build the prompt for the language model
        prompt_messages = build_prompt(history, user_text, intent_data)

        # 4. Get response from OpenAI
        assistant_response = await get_openai_response(prompt_messages)

        if not assistant_response:
            assistant_response = "Извините, у меня возникла проблема. Попробуйте еще раз."

        # Send response and save to context
        await message.answer(assistant_response)
        log_assistant_response(user_id, assistant_response)
        add_message(user_id, 'assistant', assistant_response)

    except Exception as e:
        # Generic error handling
        error_message = "Произошла непредвиденная ошибка. Мы уже работаем над этим."
        await message.answer(error_message)
        log_assistant_response(user_id, error_message)
        # Optionally log the full error for debugging
        # logging.error(f"Error handling message for user {user_id}: {e}")
    finally:
        # Ensure the user is removed from the processing set
        processing_users.remove(user_id)
