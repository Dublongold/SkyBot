
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from userform import Userform
from global_variables import *
from send_userform import *
from logger import logger
import os
#
# 8.6 Редактирование name, goal, time или links.
#
@dp.message_handler(lambda m: m.chat.id == m.from_id, state = Userform.edit_element)
async def edit_userform_element(message: Message, state: FSMContext):
    async with state.proxy() as data:
        val = data['edit_element']
        elem_name = ""
        if(val == 0):
            elem_name = "name"
        elif(val == 1):
            elem_name = "goal"
        elif(val == 2):
            elem_name = "time"
        elif(val == 3):
            elem_name = "links"
        if(elem_name != ""):
            logger(os.path.basename(__file__), "welcome", f"User with id {message.from_id} ({message.from_user.full_name}) edit {elem_name}.")
            data[elem_name] = message.text
        else:
            await bot.send_message(message.chat.id, error_message)
            return
    keyboard_buttons = [
        KeyboardButton(publish_last_answer),
        KeyboardButton(change_answer)]
    reply_keyboard_markup = ReplyKeyboardMarkup([keyboard_buttons])
    await state.set_state(Userform.want_edit)
    await bot.send_message(chat_id = message.chat.id,
                           text = lets_lock_at_result_message)
    await send_userform(
        message = message,
        state = state,
        reply_keyboard_markup = reply_keyboard_markup,
        publish = False)