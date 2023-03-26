from aiogram import Dispatcher, types
from aiogram.types import CallbackQuery

from services.db import DB
from services.fsm import FSMDialog
from services.keyboards import get_skills_keyboard

db = DB()


class EventsHandlers:
    def __init__(self, dp: Dispatcher):
        self.dp = dp

        dp.register_callback_query_handler(self.select_language_callback_handler,
                                           lambda c: c.data.startswith('select_skill'))
        dp.register_message_handler(self.companion_chat, state=FSMDialog.dialog, content_types=types.ContentType.ANY)

    async def companion_chat(self, message: types.Message):
        chat = await db.find_chat(message.chat.id)

        if chat is not None:
            chat['users'].remove(message.chat.id)
            chat_id = chat['users'][0]

            if message.text:
                await message.bot.send_message(chat_id, message.text)
            elif message.sticker:
                await message.bot.send_sticker(chat_id, message.sticker.file_id)
            elif message.video:
                await message.bot.send_video(chat_id, message.video.file_id)
            elif message.video_note:
                await message.bot.send_video_note(chat_id, message.video_note.file_id)
            elif message.voice:
                await message.bot.send_voice(chat_id, message.voice.file_id)
            elif message.photo:
                await message.bot.send_photo(chat_id, photo=message.photo[-1].file_id)
            elif message.media_group_id:
                await message.bot.send_media_group(chat_id, message.media_group_id)
            elif message.audio:
                await message.bot.send_audio(chat_id, message.audio.file_id)
            elif message.animation:
                await message.bot.send_animation(chat_id, message.animation.file_id)
            elif message.game:
                await message.bot.send_game(chat_id, game_short_name=message.game.text)
            else:
                await message.reply('**Ошибка: неизвестный тип контента**')

    async def select_language_callback_handler(self, callback_query: CallbackQuery):
        bot_skills = await db.other('bot_data', 'skills')
        skill = callback_query.data.split(':')[1]

        if skill in await db.find_user(callback_query.message.chat.id, 'skills'):
            await db.db.users.update_one({'_id': callback_query.message.chat.id}, {'$pull': {'skills': skill}})
        else:
            await db.db.users.update_one({'_id': callback_query.message.chat.id}, {'$addToSet': {'skills': skill}})

        selected_skills = await db.find_user(callback_query.message.chat.id, 'skills')
        keyboard = get_skills_keyboard(bot_skills, selected_skills)

        await callback_query.message.edit_reply_markup(keyboard)
