import json
import base64


def read_json():
    # читаем из файла
    with open('settings.json') as json_file:
        json_data = json.load(json_file)
    return json_data


def read_text(text_path) -> str:
    '''
    Чтение текста из файла
    '''
    with open(text_path, 'r') as text_file:
        text = text_file.read()
    return text


def write_text(filepath: str, text: str) -> None:
    '''
    Записывает ТОЛЬКО текст в файл
    '''
    # Убеждаемся, что text - это строка, а не байты
    if isinstance(text, bytes):
        # Если пришли байты, декодируем их
        text = text.decode('utf-8', errors='ignore')
        print(f'Warning: Received bytes, decoded to text')

    # Удаляем бинарные символы
    import re
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Записываем как обычный текст
    with open(filepath, 'w', encoding='utf-8') as out_file:
        out_file.write(text)

    print(f'Text successfully written to {filepath}')


def read_binary(binary_path: str) -> bytes:
    '''
    Чтение бинарного файла
    '''
    with open(binary_path, 'rb') as bin_file:
        binary_bytes = bin_file.read()
    return binary_bytes

# Сохранить текст по указанному пути


def save_binary(text_bytes: bytes, save_path: str) -> None:
    '''
    Сохранение текста по указанному пути
    '''
    with open(save_path, 'wb') as save_file:
        save_file.write(text_bytes)
    print("Text saved successfully!")


def save_text(text: str, save_path: str) -> None:
    '''
    Сохранение текста по указанному пути
    '''
    with open(save_path, 'w') as save_file:
        save_file.write(text)
    print("Text saved successfully!")
