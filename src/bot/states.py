from aiogram.fsm.state import State, StatesGroup


class OrderFlowers(StatesGroup):
    """
    Represents the states a user goes through when ordering flowers.
    """
    waiting_for_occasion = State()
    waiting_for_budget = State()
    waiting_for_preferences = State()
    confirming_order = State() 