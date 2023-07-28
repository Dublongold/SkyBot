from aiogram.dispatcher.filters.state import State, StatesGroup

class Userform(StatesGroup):
    name = State()
    goal = State()
    time = State()
    links = State()
    images = State()
    load_images = State()
    check = State()
    want_edit = State()
    edit = State()
    edit_process = State()
    edit_element = State()
    before_publish = State()
    cancel_token = State()