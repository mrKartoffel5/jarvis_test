import sys
import os
import json
import pyaudio
import webbrowser
from playsound import playsound
from vosk import Model, KaldiRecognizer
import time

answer_for_user = []
search_mode = False
open_mode = False
create_mode_name = False
create_mode_type = False
create_item_name = ""
create_item_type = ""


# Функция поиска файла/папки
def find_item(name):
    name = name.lower()
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    for root, dirs, files in os.walk(desktop):
        for d in dirs:
            if d.lower() == name:
                return os.path.join(root, d)
        for f in files:
            if os.path.splitext(f)[0].lower() == name:
                return os.path.join(root, f)

    for drive in ["C:\\", "D:\\", "E:\\"]:
        if not os.path.exists(drive):
            continue
        for root, dirs, files in os.walk(drive):
            for d in dirs:
                if d.lower() == name:
                    return os.path.join(root, d)
            for f in files:
                if os.path.splitext(f)[0].lower() == name:
                    return os.path.join(root, f)

    return None


# Функция создания файла или папки
def create_item(name, type_str):
    path = os.path.join(os.path.expanduser("~"), "Desktop")
    full_path = os.path.join(path, name)

    try:
        if type_str == "папка":
            if not os.path.exists(full_path):
                os.makedirs(full_path)
                print(f"Папка создана: {full_path}")
            else:
                print(f"Папка уже существует: {full_path}")
        else:  # файл с расширением
            ext_map = {
                "точка док": ".docx",
                "точка текст": ".txt",
                "точка пдф": ".pdf",
                "точка пай": ".py"
                # можно добавить другие
            }
            ext = ext_map.get(type_str.lower(), "")
            if not full_path.endswith(ext):
                full_path += ext
            if not os.path.exists(full_path):
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write("")
                print(f"Файл создан: {full_path}")
            else:
                print(f"Файл уже существует: {full_path}")
    except Exception as e:
        print("Ошибка при создании:", e)


def audio_from_micro():
    global search_mode, open_mode
    global create_mode_name, create_mode_type
    global create_item_name, create_item_type

    file_govor = 'govor.mp3'
    file_stop = 'stop.mp3'

    # --- Таймер загрузки модели ---
    print("Загрузка модели Vosk...")
    start_time = time.time()
    model = Model('vosk-model-ru-0.42')
    rec = KaldiRecognizer(model, 16000)
    end_time = time.time()
    print(f"Модель загружена за {end_time - start_time:.2f} секунд")

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1,
                    rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    playsound(file_govor)

    def listen():
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if rec.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(rec.Result())
                if answer['text']:
                    yield answer['text']

    # --- остальная логика распознавания без изменений ---
    for text in listen():
        text = text.strip()
        answer_for_user.append(text)
        print(text)

        # --- режим поиска ---
        if search_mode:
            query = text
            print(f"Поиск в Google: {query}")
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            playsound('ok.mp3')
            search_mode = False
            continue

        # --- режим открытия ---
        if open_mode:
            target = text.lower()
            print(f"Пытаюсь открыть: {target}")
            try:
                path = find_item(target)
                if path:
                    os.startfile(path)
                    playsound('ok.mp3')
                else:
                    print("Не найдено:", target)
                    playsound('no.mp3')
            except Exception as e:
                print("Ошибка открытия:", e)
                playsound('no.mp3')
            open_mode = False
            continue

        # --- режим создания ---
        if create_mode_name:
            create_item_name = text
            playsound(file_govor)  # "Какой тип? папка или файл"
            create_mode_name = False
            create_mode_type = True
            continue

        if create_mode_type:
            create_item_type = text.lower()
            create_item(create_item_name, create_item_type)
            playsound('ok.mp3')
            create_mode_type = False
            continue

        # --- стандартные команды ---
        if text == 'стоп':
            print('Вопросы пользователя:\n')
            for audio in answer_for_user:
                print(f"{audio}")
            playsound(file_stop)
            stream.stop_stream()
            stream.close()
            p.terminate()
            sys.exit()

        if text == 'привет':
            playsound('hello1.mp3')

        if text == 'ты молодец':
            playsound('thank.mp3')

        if text == 'поиск':
            playsound(file_govor)
            search_mode = True
            continue

        if text == 'открыть':
            playsound(file_govor)
            open_mode = True
            continue

        if text == 'создать':
            playsound(file_govor)  # "Что создать?"
            create_mode_name = True
            continue

def start():
    playsound('start.mp3')

if __name__ == "__main__":
    start()
    audio_from_micro()