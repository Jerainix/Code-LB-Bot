from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMReigisterUser(StatesGroup):
    makes_a_choice = State()
    change_a_choice = State()


class FSMDialog(StatesGroup):
    dialog = State()
