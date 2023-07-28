import aiogram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import (
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
    Message,
    InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio, time, datetime

from global_variables import *
from choise_what_want_to_edit import *
from edit_userform_element import *
from send_userform import *
from userform import *
from logger import logger
from cancel_token import CancellationToken
import os
# 
# Через 24 часа удаляет пользователя из забанненых на сутки и позволяет создать новую анкету.
# (Но в целях debug, несколько секунд.)
# 
async def reset_user(user_id: int, cancel_token: CancellationToken):
    logger(os.path.basename(__file__), "reset_user", f"Start wait for {user_id}.")
    await asyncio.sleep(10) # Сколько нужно ожидать перед удаление анкеты в секундах.
    if(user_id in banned_for_today_users.keys()):
        if(cancel_token.cancelled is False):
            entity_for_delete = banned_for_today_users[user_id][0]
            if(isinstance(entity_for_delete, list)):
                for message in entity_for_delete:
                    try:
                        await bot.delete_message(message.chat.id, message.message_id)
                    except:
                        pass
            else:
                try:
                    await bot.delete_message(chat_id = entity_for_delete.chat.id,
                                            message_id = entity_for_delete.message_id)
                except:
                    logger(os.path.basename(__file__), "reset_user", f"WARNING! End wait for {user_id} (deleted now, one message).")
        banned_for_today_users.pop(user_id, None)
        await bot.send_message(chat_id = user_id,
                            text = mention_message,
                            parse_mode = types.ParseMode.MARKDOWN)
        logger(os.path.basename(__file__), "reset_user", f"End wait for {user_id} (deleted now).")
    else:
        logger(os.path.basename(__file__), "reset_user", f"End wait for {user_id} (deleted previously).")

#
# Запрет написания анкет пользователями, которые уже написали анкету ранее:
#
@dp.message_handler(lambda m: m.chat.id == m.from_id and m.from_id in banned_for_today_users.keys() and m.text != delete_userform_answer)
async def user_is_banned(message: Message):
    logger(os.path.basename(__file__), "user_is_banned", f"User with id {message.from_id} ({message.from_user.full_name}) try do something ({message.text}), but he is banned.")
    await bot.send_message(chat_id = message.chat.id,
                           text = cannot_create_today_userforms_message)
# 
# При запуске бота
# 
async def on_run(_dispatcher):
    bot_data = await bot.get_me()
    logger(os.path.basename(__file__), "on_run", f"""Bot "{bot_data.full_name}" awaked.""")
from first_four_questions import *
#
# 7.5. Неправильный ввод после "Закончить"
#
@dp.message_handler(lambda m: m.chat.id == m.from_id and m.text != look_at_result_answer and m.text != publish_right_now_answer, state = Userform.check)
async def incorrect_publish_or_edit(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "publish.start", f"User with id {message.from_id} ({message.from_user.full_name}) send wrong answer (\"Закончить\").")
    await bot.send_message(chat_id = message.chat.id,
                           text = incorrect_publish_or_edit_message,
                           parse_mode = types.ParseMode.MARKDOWN)
# 
# 8. Опубликовать или изменить?
# 
@dp.message_handler(lambda m: m.chat.id == m.from_id and m.text == look_at_result_answer, state = Userform.check)
async def publish_or_edit(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "publish_or_edit", f"User with id {message.from_id} ({message.from_user.full_name}) look at his userform.") 
    keyboard_buttons = [
        KeyboardButton(publish_last_answer),
        KeyboardButton(change_answer)
    ]
    reply_keyboard_markup = ReplyKeyboardMarkup([keyboard_buttons])
    await state.set_state(Userform.want_edit)
    await send_userform(
        message = message,
        state = state,
        reply_keyboard_markup = reply_keyboard_markup,
        publish = False)
#
# 8.5 Что поменять?
#
@dp.message_handler(lambda m: m.chat.id == m.from_id and m.text == change_answer or m.text == "/change", state = [Userform.want_edit, None])
async def want_edit_userform(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "want_edit_userform", f"User with id {message.from_id} ({message.from_user.full_name}) want edit his userform.")
    keyboard_buttons = [KeyboardButton(option) for option in change_options]
    reply_keyboard_markup = ReplyKeyboardMarkup()
    for keyboard_button in keyboard_buttons:
        reply_keyboard_markup.row(keyboard_button)
    await state.set_state(Userform.edit)
    await bot.send_message(message.chat.id, what_need_to_change_message, reply_markup = reply_keyboard_markup)
#
# 8.5. Неправильный ввод после "Да!"
#
@dp.message_handler(lambda m: m.chat.id == m.from_id and m.text != change_answer and m.text != publish_last_answer, state = Userform.want_edit)
async def incorrect_publish_or_edit(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "publish.start", f"User with id {message.from_id} ({message.from_user.full_name}) send wrong answer (\"Да!\").")
    await bot.send_message(chat_id = message.chat.id,
                           text = incorrect_publish_message,
                           parse_mode = types.ParseMode.MARKDOWN)
# 
# 9. Опубликовать
# 
@dp.message_handler(lambda m: m.text == publish_last_answer and m.chat.id == m.from_id, state = Userform.want_edit)
@dp.message_handler(lambda m: m.text == publish_right_now_answer and m.chat.id == m.from_id, state = Userform.check)
async def publish(message: Message, state: FSMContext):
    if((await state.get_state()) == Userform.before_publish):
        logger(os.path.basename(__file__), "publish.start", f"User with id {message.from_id} ({message.from_user.full_name}) try published a lot of userforms.")
        return
    await state.set_state(Userform.before_publish)
    logger(os.path.basename(__file__), "publish.start", f"User with id {message.from_id} ({message.from_user.full_name}) published his userform.")
    userform_message: Message | list[Message] = await send_userform(
        message = message,
        state = state,
        reply_keyboard_markup = ReplyKeyboardRemove(),
        publish = True)
    await bot.send_photo(chat_id = message.chat.id,
                         photo = photos[5],
                         caption = userform_published_message,
                         reply_markup = ReplyKeyboardRemove(),
                         parse_mode = types.ParseMode.MARKDOWN)
    #await state.finish()
    await state.set_state(None)
    logger(os.path.basename(__file__), "publish.pre end", f"User with id {message.from_id} ({message.from_user.full_name}) banned for today.")
    cancel_token = CancellationToken()
    banned_for_today_users[message.from_id] = (userform_message, cancel_token)
    asyncio.create_task(reset_user(message.from_id, cancel_token))
    logger(os.path.basename(__file__), "publish.end", f"End work with publish for user with id {message.from_id}.")
#
# Удалить анкету
#
@dp.message_handler(lambda m: m.chat.id == m.from_id and m.text.startswith(delete_userform_answer))
async def delete_userform(message: Message):
    if(message.from_id in banned_for_today_users.keys()):
        banned_for_today_users[message.from_id][1].cancel()
        necessary_message = banned_for_today_users[message.from_id][0]
        #
        logger(os.path.basename(__file__), "delete_userform", f"User with id {message.from_id} ({message.from_user.full_name}) try delete his userform.")
        #
        if(isinstance(necessary_message, list)):
            for nm in necessary_message:
                try:
                    await bot.delete_message(chat_id = nm.chat.id,
                                             message_id = nm.message_id)
                except:
                    await bot.send_message(chat_id = message.chat.id,
                                           text = delete_userform_error_message,
                                           parse_mode = types.ParseMode.MARKDOWN)
        else:
            try:
                await bot.delete_message(chat_id = necessary_message.chat.id,
                                   message_id = necessary_message.message_id)
            except:
                await bot.send_message(chat_id = message.chat.id,
                               text = delete_userform_error_message,
                               parse_mode = types.ParseMode.MARKDOWN)
                return
        await bot.send_message(chat_id = message.chat.id,
                               text = your_userform_deleted_message,
                               parse_mode = types.ParseMode.MARKDOWN)
    else:
        await bot.send_message(chat_id = message.chat.id,
                               text = you_have_no_userform_message,
                               parse_mode = types.ParseMode.MARKDOWN)
#
# Отправить снова.
#
@dp.message_handler(lambda m: m.chat.id == m.from_id and m.text == send_again_answer, state = None)
async def send_again(message: Message, state: FSMContext):
    name = await state.get_data("name")
    goal = await state.get_data("goal")
    time = await state.get_data("time")
    links = await state.get_data("links")
    
    if(is_not_empty(name) and
       is_not_empty(goal) and
       is_not_empty(time) and 
       is_not_empty(links)):
        logger(os.path.basename(__file__), "send_again", f"User with id {message.from_id} ({message.from_user.full_name}) try send again his userform.")
        await publish(message, state)
    else:
        logger(os.path.basename(__file__), "send_again", f"User with id {message.from_id} ({message.from_user.full_name}) cannot send again his userform.")
        await bot.send_message(
            chat_id = message.chat.id,
            text = cannot_send_again_message,
            parse_mode = types.ParseMode.MARKDOWN
        )
#
# Проверить, пустая ли строкеа        
def is_not_empty(str: str) -> bool:
    return str != "" or str != None
# Начало
if( __name__ == "__main__"):
    executor.start_polling(dispatcher=dp, on_startup=on_run)