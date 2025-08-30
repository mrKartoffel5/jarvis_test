import os


def find_item(name):
    """
    Ищет папку или файл по имени (без учёта регистра) начиная с рабочего стола
    и затем по всем доступным дискам.
    Возвращает полный путь или None.
    """
    name = name.lower()

    # 1. Путь к рабочему столу текущего пользователя
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    # Сначала ищем на рабочем столе
    for root, dirs, files in os.walk(desktop):
        for d in dirs:
            if d.lower() == name:
                return os.path.join(root, d)
        for f in files:
            if os.path.splitext(f)[0].lower() == name:
                return os.path.join(root, f)

    # 2. Если не нашли на рабочем столе, ищем по всем дискам C:, D: и т.д.
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
