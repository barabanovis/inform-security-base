from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding as asymm_padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os


def symm_key_deserialize(symm_key_path: str) -> bytes:
    '''
    десериализация ключа симметричного алгоритма
    '''
    with open(symm_key_path, mode='rb') as key_file:
        content = key_file.read()

    print("Deserialized symm key type:", type(content))
    print("Deserialized symm key:", content)
    return content


def RSA_decrypt(c_text: bytes, private_key):
    '''
    дешифрование текста асимметричным алгоритмом
    '''
    dc_text = private_key.decrypt(c_text, asymm_padding.OAEP(mgf=asymm_padding.MGF1(
        algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

    print("Text decrypted!")
    print("Text: ", dc_text)
    return dc_text


def read_text(textfile_path: str):
    '''
    Чтение текста из файла
    '''
    with open(textfile_path, 'r') as textfile:
        text = textfile.read()
    return text


def text_padding(text: str) -> bytes:
    '''
    Паддинг текста
    '''
    print("=== DEBUG: Padding Process ===")
    print(f"Input text (str): {text}")

    text_bytes = text.encode('UTF-8')
    print(f"Text as bytes: {text_bytes}")
    print(f"Initial length: {len(text_bytes)} bytes")

    block_size = 16
    padding_length = block_size - (len(text_bytes) % block_size)

    if padding_length == 0:
        # Добавляем полный блок дополнения
        padding_length = block_size
        padded_text = text_bytes + b'\x00' * \
            (padding_length - 1) + bytes([padding_length])
    else:
        padded_text = text_bytes + b'\x00' * \
            (padding_length - 1) + bytes([padding_length])

    print(f"Padded text: {padded_text}")
    print(f"Padded length: {len(padded_text)} bytes")
    print(f"Is multiple of 16: {len(padded_text) % 16 == 0}")

    if len(padded_text) % 16 != 0:
        print("ERROR: Padding failed!")
    else:
        print("SUCCESS: Padding correct!")
    print("=" * 30)
    return padded_text

# Зашифровать текст по симметрическому ключу


def symm_encryption(symm_key: bytes, padded_text: bytes) -> bytes:
    """
    Шифрование текста симметричным алгоритмом 3DES-CBC.
    """
    try:
        # Проверка длины ключа для 3DES
        if len(symm_key) not in (8, 16, 24):
            raise ValueError("3DES key must be 8, 16 or 24 bytes long")

        # Генерация IV (8 байт для 3DES — размер блока 8 байт)
        iv = os.urandom(8)

        # Создание шифра с указанием бэкенда
        cipher = Cipher(
            algorithms.TripleDES(symm_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Шифрование
        c_text = encryptor.update(padded_text) + encryptor.finalize()

        # Возвращаем IV + зашифрованные данные для возможности расшифровки
        result = iv + c_text

        print("Text successfully encrypted using 3DES!")
        print("Original text length: ", len(padded_text), "bytes")
        print("Encrypted data length: ", len(result), "bytes")
        print("IV (hex): ", iv.hex())
        print("Encrypted text (hex): ", c_text.hex())

        return result

    except Exception as e:
        print(f"Encryption error: {e}")
        raise


# Сохранить текст по указанному пути
def save_text(text: bytes, save_path: str) -> None:
    '''
    Сохранение текста по указанному пути
    '''
    with open(save_path, 'wb') as save_file:
        save_file.write(text)
    print("Text saved successfully!")


def data_encryption(json_data) -> None:
    '''
    Непосредственно шифрование данных
    '''
    text_padding("my text")

    symm_key = symm_key_deserialize(json_data['symmetric_key'])
    text = read_text(json_data['initial_file'])
    text = text_padding(text)
    c_text = symm_encryption(symm_key, text)
    save_text(c_text, json_data['encrypted_file'])
