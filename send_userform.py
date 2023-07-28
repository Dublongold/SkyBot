
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from global_variables import *
from aiogram import types


async def send_userform(message: Message, state: FSMContext, reply_keyboard_markup: ReplyKeyboardMarkup | ReplyKeyboardRemove, publish: bool) -> Message | list[Message] | None:
    async with state.proxy() as data:
        links_text = data["links"].replace('_', '\\_')
        result = f"""`1. {data["name"]}
2. {data["goal"]}
3. {data["time"]}`
4. {links_text}"""
        user_images = data["images"]
        publish_chat_id = message.chat.id if (publish == None or publish == False) else necessary_chat_id
        result_message = None
        if(len(user_images) > 0):
            user_images[0].caption = result
            user_images[0].parse_mode = types.ParseMode.MARKDOWN
            result_message = await bot.send_media_group(chat_id = publish_chat_id,
                                       media = user_images)
        else:
            result_message = await bot.send_message(chat_id = publish_chat_id,
                                   text = result,
                                   parse_mode = types.ParseMode.MARKDOWN)
        if(publish == False):
            await bot.send_message(chat_id = message.chat.id,
                                   text = want_publish_or_edit_message,
                                   reply_markup = reply_keyboard_markup)
            return None
        else:
            return result_message