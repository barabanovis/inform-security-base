from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
# импорт RSA и padding для асимметричных алгоритмов
from cryptography.hazmat.primitives.asymmetric import padding as assym_padding


def symm_text_decryption(c_text: bytes, symm_key: bytes) -> str:
    try:
        # Проверка длины ключа для 3DES
        if len(symm_key) not in (8, 16, 24):
            raise ValueError("3DES key must be 8, 16 or 24 bytes long")

        # Валидация длины данных
        if len(c_text) < 16:
            raise ValueError("Ciphertext too short (needs at least 16 bytes)")

        # Извлекаем IV (первые 8 байт) и зашифрованные данные
        iv = c_text[:8]
        encrypted_data = c_text[8:]

        print(f'IV (hex): {iv.hex()}')
        print(f'Encrypted data length: {len(encrypted_data)} bytes')

        # Создаём шифр для дешифрования
        cipher = Cipher(
            algorithms.TripleDES(symm_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # Дешифрование
        padded_text = decryptor.update(encrypted_data) + decryptor.finalize()

        # Логирование для отладки
        print(f"Decrypted padded text (hex): {padded_text.hex()}")
        print(f"Last byte (padding indicator): {padded_text[-1]}")

        # Попытка депадинга с обработкой ошибок
        try:
            unpadder = padding.PKCS7(64).unpadder()
            dc_text_bytes = unpadder.update(padded_text) + unpadder.finalize()
        except ValueError as e:
            print(f"Padding removal failed: {e}")
            # Если падинг некорректен, возвращаем данные как есть (для анализа)
            dc_text_bytes = padded_text

        # Преобразование bytes в str с обработкой ошибок кодировки
        try:
            dc_text = dc_text_bytes.decode('utf-8')
        except UnicodeDecodeError:
            print("Failed to decode as UTF-8, returning hex representation")
            dc_text = f"<binary data: {dc_text_bytes.hex()}>"

        print("Text successfully decrypted using 3DES!")
        print("Decrypted text: ", dc_text)
        return dc_text

    except Exception as e:
        print(f"Decryption error: {e}")
        raise


def dc_text_unpadding(dc_text: str):
    unpadder = padding.ANSIX923(24).unpadder()
    unpadded_dc_text = unpadder.update(dc_text) + unpadder.finalize()
    return unpadded_dc_text


def symm_deserialization(symm_filepath):
    # десериализация ключа симметричного алгоритма
    with open(symm_filepath, mode='rb') as key_file:
        content = key_file.read()
    return content


def public_key_deserialize(public_pem):
    # десериализация открытого ключа
    with open(public_pem, 'rb') as pem_in:
        public_bytes = pem_in.read()
    d_public_key = load_pem_public_key(public_bytes)
    print('Public key deserialized:')
    print(d_public_key)
    return d_public_key


def private_key_deserialize(private_pem):
    # десериализация закрытого ключа
    with open(private_pem, 'rb') as pem_in:
        private_bytes = pem_in.read()
    d_private_key = load_pem_private_key(private_bytes, password=None,)
    print('Private key deserialized:')
    print(d_private_key)
    return d_private_key


def read_text(text_path) -> bytes:
    with open(text_path, 'rb') as text_file:
        text = text_file.read()
    return text


def secret_key_deserialize(pem_file_path, password=None):
    """
    Десериализует секретный ключ из PEM-файла.

    Args:
        pem_file_path (str): путь к PEM‑файлу с секретным ключом.
        password (bytes, optional): пароль для зашифрованного ключа.

    Returns:
        cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey: объект приватного ключа.

    Raises:
        ValueError: если файл не найден или ключ повреждён.
        TypeError: если пароль не соответствует формату.
        cryptography.exceptions.InvalidSignature: если подпись неверна.
    """
    try:
        with open(pem_file_path, 'rb') as pem_file:
            secret_key = pem_file.read()
        print('Secret key deserialized:')
        print(secret_key)
        return secret_key
    except FileNotFoundError:
        raise ValueError(f"Файл не найден: {pem_file_path}")
    except ValueError as e:
        raise ValueError(f"Ошибка десериализации ключа: {e}")
    except Exception as e:
        raise Exception(f"Неожиданная ошибка: {e}")


def assym_decryption(c_text, private_key):
    # дешифрование текста асимметричным алгоритмом
    dc_text = private_key.decrypt(c_text, assym_padding.OAEP(mgf=assym_padding.MGF1(
        algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    print('Assymetric decryprion algorithm returned:')
    print(dc_text)
    return dc_text


def write_text(filepath: str, text: str) -> None:
    """Записывает ТОЛЬКО текст в файл"""
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


def decryption(json_data):
    # keys deserialization
    secret_key = secret_key_deserialize(json_data['secret_key'])
    private_key = private_key_deserialize(json_data['private_key'])

    # symmetric key decryption
    symm_key = assym_decryption(secret_key, private_key)
    print('Symmetric key decrypted:')
    print(symm_key)

    # text decryption
    c_text = read_text(json_data['encrypted_file'])
    dc_text = symm_text_decryption(c_text, symm_key)
    print("Successfully decrypted text:")
    print(dc_text)
    write_text(json_data['decrypted_file'], dc_text)
