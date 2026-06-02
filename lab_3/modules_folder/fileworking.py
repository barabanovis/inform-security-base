import json
import base64
import re


def read_json():
    '''
    Чтение JSON файла с настройками
    '''
    try:
        with open('settings.json') as json_file:
            json_data = json.load(json_file)
        return json_data
    except FileNotFoundError:
        print(f"Error: File 'settings.json' not found")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}")
        raise
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        raise


def read_text(text_path) -> str:
    '''
    Чтение текста из файла
    '''
    try:
        with open(text_path, 'r') as text_file:
            text = text_file.read()
        return text
    except FileNotFoundError:
        print(f"Error: File '{text_path}' not found")
        raise
    except PermissionError:
        print(f"Error: Permission denied to read '{text_path}'")
        raise
    except Exception as e:
        print(f"Error reading text from '{text_path}': {e}")
        raise


def write_text(filepath: str, text: str) -> None:
    '''
    Записывает ТОЛЬКО текст в файл
    '''
    try:
        # Убеждаемся, что text - это строка, а не байты
        if isinstance(text, bytes):
            # Если пришли байты, декодируем их
            text = text.decode('utf-8', errors='ignore')
            print(f'Warning: Received bytes, decoded to text')

        # Удаляем бинарные символы
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

        # Записываем как обычный текст
        with open(filepath, 'w', encoding='utf-8') as out_file:
            out_file.write(text)

        print(f'Text successfully written to {filepath}')
    except PermissionError:
        print(f"Error: Permission denied to write to '{filepath}'")
        raise
    except OSError as e:
        print(f"Error: OS error while writing to '{filepath}': {e}")
        raise
    except Exception as e:
        print(f"Error writing text to '{filepath}': {e}")
        raise


def read_binary(binary_path: str) -> bytes:
    '''
    Чтение бинарного файла
    '''
    try:
        with open(binary_path, 'rb') as bin_file:
            binary_bytes = bin_file.read()
        return binary_bytes
    except FileNotFoundError:
        print(f"Error: Binary file '{binary_path}' not found")
        raise
    except PermissionError:
        print(f"Error: Permission denied to read '{binary_path}'")
        raise
    except Exception as e:
        print(f"Error reading binary from '{binary_path}': {e}")
        raise


def save_binary(text_bytes: bytes, save_path: str) -> None:
    '''
    Сохранение текста по указанному пути
    '''
    try:
        with open(save_path, 'wb') as save_file:
            save_file.write(text_bytes)
        print("Text saved successfully!")
    except PermissionError:
        print(f"Error: Permission denied to write to '{save_path}'")
        raise
    except TypeError:
        print(f"Error: Expected bytes, got {type(text_bytes).__name__}")
        raise
    except Exception as e:
        print(f"Error saving binary to '{save_path}': {e}")
        raise


def save_text(text: str, save_path: str) -> None:
    '''
    Сохранение текста по указанному пути
    '''
    try:
        with open(save_path, 'w') as save_file:
            save_file.write(text)
        print("Text saved successfully!")
    except PermissionError:
        print(f"Error: Permission denied to write to '{save_path}'")
        raise
    except TypeError:
        print(f"Error: Expected str, got {type(text).__name__}")
        raise
    except Exception as e:
        print(f"Error saving text to '{save_path}': {e}")
        raise
