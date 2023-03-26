from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from services.db import DB
from services.fsm import FSMReigisterUser
from services.keyboards import get_skills_keyboard, reply_keyboard, general_keyboard

db = DB()


class RegistrationHandlers:
    def __init__(self, dp: Dispatcher):
        self.dp = dp

        dp.register_message_handler(self.start, commands=['start'], state=None)
        dp.register_message_handler(self.user_choice, Text(equals=['Я ищу кому помочь', 'Мне нужна помощь']),
                                    state=FSMReigisterUser.makes_a_choice)
        dp.register_message_handler(self.edit_skills, Text(equals='Ваши скиллы'))
        dp.register_message_handler(self.change_choice_command, Text(equals='Изменить выбор'))
        dp.register_message_handler(self.change_choice, Text(equals=['Я ищу кому помочь', 'Мне нужна помощь']),
                                    state=FSMReigisterUser.change_a_choice)

    async def start(self, message: types.Message):
        user = await db.find_user(message.chat.id)

        if user is None:
            await FSMReigisterUser.makes_a_choice.set()
            await message.reply('Сделайте выбор при помощи кнопок',
                                reply_markup=reply_keyboard(['Я ищу кому помочь', 'Мне нужна помощь']))
        else:
            await message.reply('Чем могу помочь?', reply_markup=general_keyboard())

    async def user_choice(self, message: types.Message, state: FSMContext):
        await message.reply('**Ваш ответ успешно занесён в базу данных**', reply_markup=general_keyboard())

        choice = 'helper' if message.text == 'Я ищу кому помочь' else 'need_help'
        current_state = await state.get_state()
        data_skills = await db.other('bot_data', 'skills')

        await db.add_user(message.chat.id, choice)
        await state.finish()
        await message.reply('Выберите ваши скиллы\nМы будем искать собеседника основываясь на ваших скиллов',
                            reply_markup=get_skills_keyboard(data_skills, []))

    async def edit_skills(self, message: types.Message):
        user_skills = await db.find_user(message.chat.id, 'skills')
        data_skills = await db.other('bot_data', 'skills')
        await message.reply('Выберите ваши скиллы\nМы будем искать собеседника основываясь на ваших скиллов',
                            reply_markup=get_skills_keyboard(data_skills, user_skills))

    async def change_choice_command(self, message: types.Message):
        await FSMReigisterUser.change_a_choice.set()
        await message.reply('Сделайте выбор при помощи кнопок',
                            reply_markup=reply_keyboard(['Я ищу кому помочь', 'Мне нужна помощь']))

    async def change_choice(self, message: types.Message, state: FSMContext):
        choice = 'helper' if message.text == 'Я ищу кому помочь' else 'need_help'

        await state.finish()
        await db.db.users.update_one({'_id': message.chat.id}, {'$set': {'choice': choice}})
        await message.reply(f'Ваш выбор успешно изменён на: {choice}', reply_markup=general_keyboard())
