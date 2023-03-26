from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from services.db import DB
from services.fsm import FSMDialog
from services.keyboards import reply_keyboard, general_keyboard, dialog_keyboard

db = DB()


class DialogHandlers:
    def __init__(self, dp: Dispatcher):
        self.dp = dp

        dp.register_message_handler(self.search_dialog, Text(equals='Найти собеседника'))
        dp.register_message_handler(self.stop_searching_dialog, Text(equals='Остановить поиск'))
        dp.register_message_handler(self.stop_dialog, Text(equals='Остановить диалог'), state=FSMDialog.dialog)
        dp.register_message_handler(self.next_dialog, Text(equals='Следующий собеседник'), state=FSMDialog.dialog)
        dp.register_message_handler(self.search_dialog, Text(equals='Найти собеседника'))
        dp.register_message_handler(self.stop_dialog, commands=['stop'], state=FSMDialog.dialog)
        dp.register_message_handler(self.next_dialog, commands=['next'], state=FSMDialog.dialog)

    async def search_dialog(self, message: types.Message, state: FSMDialog):
        user_data = await db.find_user(message.chat.id)
        queue_user = await db.db.queue.find_one(
            {'choice': {'$ne': user_data['choice']}, 'skills': {'$in': user_data['skills']}})
        companion = await db.find_companion(message.chat.id, user_data['choice'], user_data['skills'])

        if companion:

            msg_text = """**Мы нашли для вас собеседника!**
                \nЕго скиллы: %s
                \n/next - найти другого пользователя
                \n/stop - завершить диалог"""

            await message.bot.send_message(message.chat.id, msg_text % ', '.join(user_data['skills']),
                                           reply_markup=dialog_keyboard())
            await message.bot.send_message(queue_user['_id'], msg_text % ', '.join(queue_user['skills']),
                                           reply_markup=dialog_keyboard())
            await FSMDialog.dialog.set()
            companion_fsm = self.dp.current_state(user=queue_user['_id'], chat=queue_user['_id'])
            await companion_fsm.set_state(FSMDialog.dialog.state)
        else:
            await message.reply(text='**Ищем собеседника...**', reply_markup=reply_keyboard(['Остановить поиск']))

    async def stop_dialog(self, message: types.Message, state: FSMContext):
        chat = await db.find_chat(message.chat.id)

        await db.db.chats.delete_one({'users': {'$in': [message.chat.id]}})

        for user in chat['users']:
            companion_fsm = self.dp.current_state(user=user, chat=user)
            await companion_fsm.finish()
            await message.bot.send_message(user, '**Диалог завершён**', reply_markup=general_keyboard())

    async def next_dialog(self, message: types.Message, state: FSMContext):
        await self.stop_dialog(message, state)
        await self.search_dialog(message, state)

    async def stop_searching_dialog(self, message: types.Message):
        user_in_queue = await db.find_queue(message.chat.id)

        if user_in_queue is not None:
            await db.db.queue.delete_one({'_id': message.chat.id})
            await message.reply('**Поиск остановлен**', reply_markup=general_keyboard())
