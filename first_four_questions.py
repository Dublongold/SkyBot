import aiogram, os
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext
from userform import Userform
from global_variables import *
from send_userform import *
from aiogram.types import ContentType
from threading import Lock
from logger import logger
#
# 1. Приветствие:
#
@dp.message_handler(lambda m: m.chat.id == m.from_id and m.text in start_commands)
async def welcome(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "welcome", f"User with id {message.from_id} ({message.from_user.full_name}) write start.")
    keyboard_buttons = [
        KeyboardButton(lets_go_answer),
        KeyboardButton(maybe_letter_answer)
    ]
    await state.set_state(Userform.name)
    reply_keyboard_markup = ReplyKeyboardMarkup([keyboard_buttons])
    await bot.send_photo(photo=photos[0],
                        chat_id=message.chat.id,
                        caption=welcome_message.format(message.from_user.full_name),
                        reply_markup=reply_keyboard_markup)
#
# 2. Имя:
#
@dp.message_handler(lambda m: m.from_id == m.chat.id and (m.text == lets_go_answer or m.text == maybe_letter_answer) and m.text != delete_userform_answer and m.text != send_again_answer, state = [Userform.name, None])
async def lest_go_and_get_name(message: Message, state: FSMContext):
    chat_member_status = await bot.get_chat_member(necessary_chat_id, message.from_id)
    if(chat_member_status["status"] in subscribe_status):
        logger_message_end = ""
        if(message.text in start_commands):
            logger_message_end = "start."
            await welcome(message, state)
        elif(message.text == lets_go_answer):
            logger_message_end = f'"{lets_go_answer}"'
            await state.set_state(Userform.goal)
            await bot.send_photo(chat_id=message.chat.id,
                                photo = photos[1],
                                caption = user_name_message, reply_markup=ReplyKeyboardRemove())
        elif(message.text == maybe_letter_answer):
            logger_message_end = f'"{maybe_letter_answer}"'
            await bot.send_message(chat_id=message.chat.id,
                                text = welcome_maybe_letter_message,
                                parse_mode=aiogram.types.ParseMode.MARKDOWN)
        else:
            logger_message_end = f"wrong answer ({message.text})"
            await bot.send_message(chat_id=message.chat.id,
                                text = wrong_message_text)
        logger(os.path.basename(__file__), "welcome", f"User with id {message.from_id} ({message.from_user.full_name}) ({message.from_user.full_name}) write {logger_message_end}")
    else:
        logger(os.path.basename(__file__), "welcome", f"User with id {message.from_id} ({message.from_user.full_name}) unsubscribed. Status: {chat_member_status['status']}")
        buttons = [
            InlineKeyboardButton("Подписаться", url="https://t.me/+raC4OyN9K3tlNzMy")
            ]
        inline_markup = InlineKeyboardMarkup()
        inline_markup.row(buttons[0])
        await bot.send_message(message.chat.id,
                               please_subscribe,
                               reply_markup = inline_markup)
#
# 3. Цель:
#
@dp.message_handler(lambda m: m.chat.id == m.from_id, state = Userform.goal)
async def get_user_goal(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "welcome", f"User with id {message.from_id} ({message.from_user.full_name}) write his name ({message.text}).")
    async with state.proxy() as data:
        data['name'] = message.text
    await state.set_state(Userform.time)
    await bot.send_photo(chat_id=message.chat.id, photo = photos[2], caption = user_goal_message, reply_markup=ReplyKeyboardRemove())

#
# 4. Время:
#
@dp.message_handler(lambda m: m.chat.id == m.from_id, state = Userform.time)
async def get_userform_actuality(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "welcome", f"User with id {message.from_id} ({message.from_user.full_name}) write his goal ({message.text}).")
    async with state.proxy() as data:
        data['goal'] = message.text
    await state.set_state(Userform.links)
    await bot.send_photo(chat_id=message.chat.id, photo = photos[3], caption = userform_actuality_message, reply_markup=ReplyKeyboardRemove())
#
# 5. Ссылки:
#
@dp.message_handler(lambda m: m.chat.id == m.from_id, state = Userform.links)
async def get_where_to_go_to_user(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "welcome", f"User with id {message.from_id} ({message.from_user.full_name}) write his time ({message.text}).")
    async with state.proxy() as data:
        data['time'] = message.text
    await state.set_state(Userform.images)
    await bot.send_photo(chat_id=message.chat.id, photo = photos[4], caption = where_to_go_to_user_message, reply_markup=ReplyKeyboardRemove())
#
# 6. Картинка/Картинки.
#
@dp.message_handler(lambda m: m.chat.id == m.from_id, state = Userform.images)
async def attach_projects_or_not(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "welcome", f"User with id {message.from_id} ({message.from_user.full_name}) write his links ({message.text}).")
    async with state.proxy() as data:
        data['links'] = message.text
        data['images'] = []
    await state.set_state(Userform.load_images)
    keyboard_buttons = [KeyboardButton(end_creating_userform_answer)]
    reply_keyboard_markup = ReplyKeyboardMarkup([keyboard_buttons])
    await bot.send_message(
        chat_id=message.chat.id,
        text = user_image_message, 
        reply_markup=reply_keyboard_markup,
        parse_mode=types.ParseMode.MARKDOWN)
#
# 6.5. Загрузка изображений.
#
lock = Lock()
@dp.message_handler(lambda m: m.chat.id == m.from_id, state = Userform.load_images, content_types=[ContentType.PHOTO, ContentType.VIDEO])
async def take_images(message: Message, state: FSMContext):
    lock.acquire()
    for_logger = "-1"
    if(message.content_type == ContentType.PHOTO):
        for_logger = message.photo[-1].file_unique_id
    elif(message.content_type == ContentType.VIDEO):
        for_logger = message.video.file_unique_id
    logger(os.path.basename(__file__), "welcome", f"User with id {message.from_id} ({message.from_user.full_name}) load mediafile with unique id {for_logger}.")
    image_count = 0
    text_to_send = ""
    async with state.proxy() as data:
        image_count = len(data["images"])
        if(image_count < 10):
            if(message.content_type == ContentType.VIDEO):
                data["images"].append(types.InputMediaVideo(message.video.file_id))
            elif(message.content_type == ContentType.PHOTO):
                data["images"].append(types.InputMediaPhoto(message.photo[-1].file_id))
            else:
                print(message.content_type)
            text_to_send = image_has_been_added_message.format(len(data['images']))
            image_count += 1
        else:
            text_to_send = images_limit_message
    lock.release()
    await bot.send_message(chat_id = message.chat.id,
                            text = text_to_send,
                            parse_mode=types.ParseMode.MARKDOWN)
    
#    
# 7. Посмотреть или опубликовать?
#        
@dp.message_handler(lambda m: m.chat.id == m.from_id and m.text == end_creating_userform_answer, state = Userform.load_images, content_types=ContentType.TEXT)
async def check_or_publish(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "welcome", f"User with id {message.from_id} ({message.from_user.full_name}) write \"{end_creating_userform_answer}\".")
    keyboard_buttons = [
        KeyboardButton(look_at_result_answer),
        KeyboardButton(publish_right_now_answer)
    ]
    reply_keyboard_markup = ReplyKeyboardMarkup([keyboard_buttons])
    await state.set_state(Userform.check)
    await bot.send_message(chat_id=message.chat.id,
                           text = look_at_result_message,
                           reply_markup=reply_keyboard_markup)
#    
# 7.5. Отправлен текст, а не изображение
#        
@dp.message_handler(lambda m: m.chat.id == m.from_id and m.text != end_creating_userform_answer, state = Userform.load_images, content_types=ContentType.TEXT)
async def check_or_publish(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "welcome", f"User with id {message.from_id} ({message.from_user.full_name}) write \"{message.text}\".")
    await bot.send_message(chat_id=message.chat.id,
                           text = text_instead_image_message)
