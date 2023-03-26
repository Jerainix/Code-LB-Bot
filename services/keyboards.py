from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup


def get_skills_keyboard(skills: list, selected_skills: list) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)

    for skill in skills:
        if skill in selected_skills:
            button_text = f"{skill} ✅"
        else:
            button_text = skill

        callback_data = f"select_skill:{skill}"
        button = InlineKeyboardButton(button_text, callback_data=callback_data)
        keyboard.insert(button)
    return keyboard


def reply_keyboard(buttons: list, one_time_keyboard: bool = False):
    keyword = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time_keyboard)

    for button_text in buttons:
        button = KeyboardButton(button_text)
        keyword.add(button)
    return keyword


def general_keyboard():
    return reply_keyboard(['Найти собеседника', 'Ваши скиллы', 'Изменить выбор'])


def dialog_keyboard():
    return reply_keyboard(['Следующий собеседник', 'Остановить диалог'])
