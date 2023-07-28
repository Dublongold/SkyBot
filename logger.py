import datetime, os

#
# Призначен для debug вывода информации в консоль..
#
def logger(source: str, function: str | None, message: str, *additional_information: str):
    """Более читабельный и удобный вывод информации.\n\n
• source - обычно, файл, в котором запущен логгер.\n
• function - функция, в котором запущен логгер. Если нету, передать None.\n
• message - сообщенние, которое нужно вывести."""
    print(f"""[{datetime.datetime.now()}] ({source}){' "' + function + '" ' if (function != None) else ""}: {message}""")