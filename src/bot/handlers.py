import logging
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from src.assistant.openai_client import get_openai_response, get_intent_from_openai
from src.assistant.prompts import build_prompt
from src.bot.routers import main_router
from src.bot.states import OrderFlowers
from src.database.database import async_session_maker, get_or_create_user


@main_router.message(StateFilter(None))
async def route_message(message: types.Message, state: FSMContext):
    """
    This is the main router for incoming messages from users without an active state.
    It determines the user's intent and starts the appropriate FSM scenario.
    """
    user_id = message.from_user.id
    user_name = message.from_user.username or message.from_user.first_name
    user_text = message.text

    # Update user stats
    async with async_session_maker() as session:
        await get_or_create_user(session, user_id, user_name)

    # Get intent from NLU
    intent_data = await get_intent_from_openai(user_text)
    intent = intent_data.get("intent", "unknown") if intent_data else "unknown"
    entities = intent_data.get("entities", {}) if intent_data else {}


    # --- Intent-based Routing ---
    if intent in ["order_flowers", "ask_for_recommendation"]:
        # Check if the occasion was already extracted
        if "occasion" in entities:
            await state.update_data(occasion=entities["occasion"])
            await state.set_state(OrderFlowers.waiting_for_budget)
            await message.answer(f"Отлично, подбираем букет для случая: \"{entities['occasion']}\". Какой у вас бюджет?")
        else:
            await state.set_state(OrderFlowers.waiting_for_occasion)
            await message.answer("Конечно! Давайте подберем букет. Для какого случая он нужен?")
    
    elif intent == "greeting":
        await message.answer("Здравствуйте! Чем могу помочь? Вы хотите заказать цветы или нужна рекомендация?")
    else:
        # Fallback to a general response for unhandled intents
        # For now, we'll use the generic OpenAI response
        prompt = build_prompt([], user_text)
        response = await get_openai_response(prompt)
        await message.answer(response or "Я вас не совсем понял. Могу ли я помочь с выбором цветов?")

# --- FSM Handlers for Ordering Flowers ---

@main_router.message(OrderFlowers.waiting_for_occasion, F.text)
async def process_occasion(message: types.Message, state: FSMContext):
    """Handles the user's response about the occasion for the flowers."""
    await state.update_data(occasion=message.text)
    await state.set_state(OrderFlowers.waiting_for_budget)
    await message.answer("Отлично! А какой бюджет вы планируете?")


@main_router.message(OrderFlowers.waiting_for_budget, F.text)
async def process_budget(message: types.Message, state: FSMContext):
    """Handles the user's response about the budget."""
    await state.update_data(budget=message.text)
    await state.set_state(OrderFlowers.waiting_for_preferences)
    await message.answer("Понял. Есть ли какие-то особые предпочтения по цветам или, может быть, по настроению букета?")


@main_router.message(OrderFlowers.waiting_for_preferences, F.text)
async def process_preferences(message: types.Message, state: FSMContext):
    """
    Handles user's preferences, generates a final recommendation using AI,
    and moves to the confirmation state.
    """
    await state.update_data(preferences=message.text)
    user_data = await state.get_data()

    # Build a detailed prompt for the AI assistant
    recommendation_prompt = (
        f"Сгенерируй предложение букета для клиента со следующими данными:\n"
        f"- Повод: {user_data.get('occasion')}\n"
        f"- Бюджет: {user_data.get('budget')}\n"
        f"- Предпочтения: {user_data.get('preferences')}\n"
        f"Предложи один конкретный, красивый вариант, дай ему название и опиши состав. "
        f"Закончи вопросом, подходит ли клиенту это предложение."
    )

    # We use build_prompt to add the system persona
    final_prompt = build_prompt([], recommendation_prompt)
    
    await message.answer("Отлично, я подбираю для вас идеальный вариант... Пожалуйста, подождите немного.")

    recommendation = await get_openai_response(final_prompt)

    await state.update_data(recommendation=recommendation)
    await state.set_state(OrderFlowers.confirming_order)
    
    await message.answer(recommendation or "К сожалению, не смог подобрать вариант. Попробуем еще раз?")


@main_router.message(OrderFlowers.confirming_order, F.text)
async def process_confirmation(message: types.Message, state: FSMContext):
    """
    Handles the user's confirmation.
    Finishes the FSM scenario.
    """
    user_response = message.text.lower()
    
    if "да" in user_response or "подходит" in user_response or "согласен" in user_response:
        await message.answer("Отлично! Рад, что вам понравилось. Вскоре мы добавим функцию оформления заказа, а пока вы можете передать этот диалог менеджеру.")
    else:
        await message.answer("Жаль, что предложение не подошло. Мы можем попробовать подобрать другой вариант или вы можете пообщаться с нашим флористом напрямую.")
        
    # Clear the state to finish the scenario
    await state.clear()


@main_router.message(F.content_type.in_({'photo', 'document', 'audio', 'sticker', 'video', 'voice'}))
async def handle_unsupported_content(message: types.Message):
    """
    Handles all non-text content types with a polite message.
    """
    await message.answer("К сожалению, я умею работать только с текстом. Пожалуйста, опишите ваш запрос словами.")
