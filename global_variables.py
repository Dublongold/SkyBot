from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import re
from cancel_token import CancellationToken

TOKEN = "5174323264:AAGJ2hDudNi_Is1_oWCCuSDe_uvC-yHzh9A"
"""Токен бота."""
necessary_chat_id = "-896294984"
"""ID - чата, куда публиковать анкеты."""
day_in_seconds = 86400
"""24 часа в секундах"""
start_commands =[
    "/start",
    "начать",
    "старт"
]
"""Команды /start."""
subscribe_status = [
    "creator",
    "administrator",
    "member"
]
"""Нужные состояния пользователя, чтобы начать создавать анкету."""
banned_for_today_users: dict[int, tuple[Message | list[Message], CancellationToken]] = {}
"""Пользователи, которые уже создали анкету и не имеют доступа к созданию новой пока не пройдёт 24 часа с момента создания последней анкеты."""

# Сообщения, которые отправляет бот:
# 
#   Сообщение приветствия.
welcome_message =\
"""Привет, {}!
Я - Отшельник-обниматель и я помогу тебе составить анкету в сервис "Сердце к сердцу"

Составим анкету?
Но для начала спешу ведомить, что вы должны подписаться на канал ЛЯ-ЛЯ-ЛЯ, чтобы у вас получилось создать анкету.""" # {} - это место, где будет никнейм пользователя.
#   Когда пользователь ответил "Может, позже":
welcome_maybe_letter_message = """Спасибо, что обратились! Буду ждать, когда снова стану вам полезен.
Когда заходите составить антету, просто отправьте мне `Приступим!`."""
#   Когда пользователь неподписан на нужные каналы.
please_subscribe =\
"""Пожалуйста, подпишитесь на канал ЛЯ-ЛЯ-ЛЯ, чтобы у вас получилось создать анкету."""
#   Когда пользователь ответил неправильно.
wrong_message_text =\
"Я вас не понимаю..."
# 
#   Сообщение для получения имени пользователя.
user_name_message =\
"Окей. Теперь мы пожем начать составление анкеты. Как к вам обращаться? Небольшая памятка поможет вам в этом."
#   Сообщения для получения цели пользователя.
user_goal_message =\
"""Цель, которая будет указана в анкете."""
#   Сообщения для получения времени
userform_actuality_message =\
"""Время, в течение которого анкета будет актуальна."""
#   Сообщения для получения места куда обращаться
where_to_go_to_user_message =\
"""Куда обращаться?"""
#
#   Сообщения для получения картинок пользователя
user_image_message =\
"""Прикрепите картинку для привлечения внимания.

Этот шаг можно пропустить, отправив мне `Закончить!`."""
#   Сообщение об достижении лимита загружаемых картинок.
images_limit_message =\
"""Вы уже добавили максимальное количество изображений.
Чтобы закончить, отправьте `Закончить!`."""
#   Сообщение об успешном добавлении картинки.
image_has_been_added_message =\
"""{}-я по порядку медиафайл из 10 возможных сохраннен.
Если вы добавили достаточно, отправьте `Закончить!`.""" #Вместо {} в будущем будет порядок добавленой картинки.
#   Сообщение об неверном вводе при приёме картинок.
text_instead_image_message =\
"""Я вас не понимаю...
Если вы хотите закончить, отправьте `Закончить!`, а если нет, то отправьте мне медиафайл."""
#
#   Сообщение, предлагающее посмотреть на результат.
look_at_result_message =\
"Отлично! Посмотрим, что у Вас получилось?"
#
#   Сообщение об неверном вводе перед проверкой анкеты.
incorrect_publish_or_edit_message =\
"""Я вас не понимаю... Вы хотите посмотреть на то, что у вас получилось(`Да!`), или опубликовать сразу(`Опубликовать сразу`)?"""
#
#   Сообщение об неверном вводе перед публикацией или редактированием.
incorrect_publish_message =\
"""Я вас не понимаю... Вы хотите редактировать вашу анкету(`Изменить`), или опубликовать (`Опубликовать!`)?"""
#
#   Сообщение, спрашивающее опубликовать или изменить.
want_publish_or_edit_message =\
"Хотите опубликовать Вашу анкету или изменить её?"
#
#   Сообщение, спрашивающее о том, что нужно изменить.
what_need_to_change_message =\
"Что именно Вы хотите изменить?"
#
#   Запросы на тот элемент анкеты, который нужно изменить.
change_element_messages = [
    "Хорошо, введите имя/никнейм:",
    "Хорошо, введите цель:",
    "Хорошо, введите время заново:",
    "Хорошо, введите куда обращаться заново:"
]
#
lets_lock_at_result_message =\
"Хорошо, теперь давайте посмотрим на результат:"
#
#
#   Сообщение, уведомляющее об опубликации анкеты.
userform_published_message =\
"""Анкета опубликована! 💫

Завтра с обновлением дня Вы сможете опубликовать новую анкету."""
#
#   Сообщение - напоминание.
mention_message =\
"""Нaпоминание!
Новый день - новая анкета! 💞
Чтобы её создать, отправьте мне `Приступим!`.
А если вы хотите отправить анкету с вашими данными снова, то просто отправите `Отправить снова`"""
#   Сообщение, которое говорит об перезаписи анкеты.
lets_rewrite_userform_message =\
"""Окей, давайте начнём сначала.
Как к вам обращаться? Небольшая памятка поможет вам в этом."""
#
#   Сообщение, которое уведомляет о невозможности написать новую анкету.
cannot_create_today_userforms_message =\
"""Извините, но Вы не можете пока что создавать новые анкеты.
Дождитесь, когда я отправлю Вам напоминание, после которого вы сможете уже написать свою новую анкету."""
#
#   Сообщение - ошибка.
error_message =\
"Ошибка..."
#
#   Сообщение, уведомляющее о отсутствии анкет пользователя.
you_have_no_userform_message =\
"""Вы не написали ещё анкету или ваша анкета уже была удалена ранее, так что не можете её удалить.
Зато вы можете написать новую Вашу анкету, отправив мне `Приступим!`"""
#   Анкета удалена успешно
your_userform_deleted_message =\
"Хорошо, ваша анкета удалена.\nТеперь вы можете написать новую анкету, отправив мне `Приступим!`."
#   Не удалось удалить анкету
delete_userform_error_message =\
"""Простите, но не удалось удалить вашу анкету...
Зато вы можете написать новую, отправив мне `Приступим!`!"""
# Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!Update!
#   Нельзя отправить анкету снова
cannot_send_again_message =\
"Извините, но вы ранее не создавали анкеты. Чтобы создать анкету, отправьте мне `Приступим!`"
# 
# Варианты ответов пользователя:
#
#   После приветствия:
lets_go_answer =\
"Приступим!"
maybe_letter_answer =\
"Может, потом"
#   Удалить анкету:
delete_userform_answer =\
"/удалить"
#   После/До отправки картинок.
end_creating_userform_answer = "Закончить!"
#   Посмотреть на результат.
look_at_result_answer =\
"Да!"
#   Опубликовать(сразу, даже не смотря на результат).
publish_right_now_answer =\
"Опубликовать сразу"
#   Опубликовать(после просмотра результата).
publish_last_answer =\
"Опубликовать!"
#   Изменить анкету.
change_answer =\
"Изменить"
#   Варианты того, что можно изменить.
change_options =[
"Имя",
"Цель",
"Время",
"Ссылки",
"Картинки",
"Начать заново",
"Я передумал"]
#   Отправить снова
send_again_answer =\
"Отправить снова"
bot = Bot(token=TOKEN)
"""Сам бот, который работает."""
memory_storage = MemoryStorage()
"""Нужно для хранения состояния пользователя."""
dp = Dispatcher(bot=bot, storage=memory_storage)
"""Нужно для управления поведением бота."""

file_names = ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.png"]
"""Название файлов-картинок, которые будет отправилять бот."""
photos: list[bytes] = []
"""После запуска бота, тут будут файлы-картинки в нужном формате для вывода пользователю."""
# Из файла конвертируется изображение в байты, после чего можна будет отправлять его пользователю.
import os
for i in file_names:
    full_path = re.sub("\w+\.py", "", __file__)
    with(open(full_path + f"images{os.sep}{i}") as f):
        photos.append(f.buffer.read())
        