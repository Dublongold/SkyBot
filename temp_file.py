#
#   Сообщение об неверном вводе перед проверкой анкеты.
incorrect_publish_or_edit_message =\
"""Я вас не понимаю... Вы хотите посмотреть на то, что у вас получилось(`Да!`), или опубликовать сразу(`Опубликовать сразу`)?"""
#
#   Сообщение об неверном вводе перед публикацией или редактированием.
incorrect_publish_message =\
"""Я вас не понимаю... Вы хотите редактировать вашу анкету(`Изменить`), или опубликовать (`Опубликовать!`)?"""

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
# 8.5. Неправильный ввод после "Да!"
#
@dp.message_handler(lambda m: m.chat.id == m.from_id and m.text != change_answer and m.text != publish_last_answer, state = Userform.want_edit)
async def incorrect_publish_or_edit(message: Message, state: FSMContext):
    logger(os.path.basename(__file__), "publish.start", f"User with id {message.from_id} ({message.from_user.full_name}) send wrong answer (\"Да!\").")
    await bot.send_message(chat_id = message.chat.id,
                           text = incorrect_publish_message,
                           parse_mode = types.ParseMode.MARKDOWN)