
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from userform import Userform
from global_variables import dp
from global_variables import *
from logger import logger
import os
#
# Изменения елементов (имя, цель, ссылки и т. д.) анкеты.
#
@dp.message_handler(lambda m: m.chat.id == m.from_id, state = Userform.edit)
async def choise_what_to_want_edit(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "welcome", f"User with id {message.from_id} choise what he want to edit.")
    user_text = message.text
    async with state.proxy() as data:
        if(user_text in change_options[:4]):
            data['edit_element'] = change_options.index(user_text)
            await state.set_state(Userform.edit_element)
            await bot.send_message(chat_id = message.chat.id,
                                   text = change_element_messages[data['edit_element']],
                                   reply_markup = ReplyKeyboardRemove())
        if(user_text == change_options[4]):
            await state.set_state(Userform.load_images)
            keyboard_buttons = [KeyboardButton(end_creating_userform_answer)]
            reply_keyboard_markup = ReplyKeyboardMarkup([keyboard_buttons])
            data['images'] = []
            await bot.send_message(
                chat_id = message.chat.id,
                text = user_image_message, 
                reply_markup = reply_keyboard_markup)
    if(user_text == change_options[5]):
        await state.reset_data()
        await state.set_state(Userform.goal)
        await bot.send_photo(chat_id = message.chat.id,
                             photo = photos[1],
                             caption = lets_rewrite_userform_message,
                             reply_markup = ReplyKeyboardRemove())
    if(user_text == change_options[6]):
        keyboard_buttons = [
            KeyboardButton(look_at_result_answer),
            KeyboardButton(publish_right_now_answer)
        ]
        reply_keyboard_markup = ReplyKeyboardMarkup([keyboard_buttons])
        await state.set_state(Userform.check)
        await bot.send_message(chat_id = message.chat.id,
                               text = look_at_result_message,
                               reply_markup = reply_keyboard_markup)