from typing import List, Dict, Any, Optional

# --- System Prompt ---
# This defines the persona and instructions for the AI assistant.
SYSTEM_PROMPT = """
Вы - профессиональный продавец-консультант в цветочном магазине. Ваша задача - помочь клиенту выбрать идеальный букет.
1. Будьте дружелюбны, но профессиональны
2. Задавайте уточняющие вопросы, чтобы понять потребности клиента
3. Предлагайте конкретные варианты на основе ответов
4. Помогайте с оформлением заказа
5. Используйте профессиональную лексику флориста
Пример хорошего ответа:
"Для романтического вечера я рекомендую наш букет 'Нежность' из розовых пионов и белых эустом. Какой бюджет вы рассматриваете?"
"""

NLU_SYSTEM_PROMPT = """
Вы - модель NLU для цветочного магазина. Анализируйте сообщение пользователя и определяйте намерение.
Отвечайте JSON объектом с полями 'intent' и 'entities'.
Возможные намерения:
"greeting" - приветствие
"farewell" - прощание  
"order_flowers" - заказ цветов
"ask_for_recommendation" - запрос рекомендации
"check_delivery_status" - проверка статуса доставки
"ask_about_payment" - вопросы по оплате
"unknown" - неизвестное намерение

Примеры:
User: "Здравствуйте, хочу заказать букет"
Assistant: {"intent": "order_flowers", "entities": {}}

User: "Посоветуйте цветы на день рождения"
Assistant: {"intent": "ask_for_recommendation", "entities": {"occasion": "день рождения"}}

User: "Когда привезут мой заказ?"
Assistant: {"intent": "check_delivery_status", "entities": {}}
"""


def build_prompt(history: List[Dict[str, str]], user_text: str, intent_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    """
    Собирает список сообщений для вызова OpenAI API.

    :param history: История диалога
    :param user_text: Текущее сообщение пользователя
    :param intent_data: Данные о намерении от NLU
    :return: Список сообщений в формате для API
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)

    if intent_data and intent_data.get("intent") != "unknown":
        content = user_text
    else:
        content = user_text

    formatted_user_message = {"role": "user", "content": content}

    messages.append(formatted_user_message)
    return messages
