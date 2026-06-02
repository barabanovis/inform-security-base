from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
# импорт RSA и padding для асимметричных алгоритмов
from cryptography.hazmat.primitives.asymmetric import padding as assym_padding

import modules_folder.fileworking as fw


def symm_text_decryption(c_text: bytes, symm_key: bytes) -> str:
    '''
    Дешифровка текста симметричным алгоритмом: в данном случае 3DES

    Args:
        c_text (bytes): Зашифрованные данные в формате байтов, которые включают:
                       - IV (вектор инициализации) - первые 8 байт
                       - Зашифрованный текст (остальные байты)
                       Данные должны быть получены из функции symm_encryption()

        symm_key (bytes): Симметричный ключ для дешифрования.
                         Должен быть длиной 8, 16 или 24 байта (для 3DES).
                         Обычно 24 байта для Triple DES с 3 ключами.

    Returns:
        str: Расшифрованный текст в виде строки (без паддинга)

    Raises:
        ValueError: Если длина ключа не соответствует требованиям 3DES
                   или если данные имеют неверный формат
        Exception: При ошибках дешифрования (неправильный ключ, 
                  поврежденные данные и т.д.)
    '''
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
    '''
    Депаддинг дешифрованного текста

    Параметры:
        dc_text (str): Дешифрованный текст с добавленным padding'ом ANSI X9.23.
                       Должен иметь длину, кратную 24 байтам (размер блока).
                       Последний байт указывает количество добавленных байт padding'а.

    Возвращает:
        str: Исходный текст без padding'а
    '''
    unpadder = padding.ANSIX923(24).unpadder()
    unpadded_dc_text = unpadder.update(dc_text) + unpadder.finalize()
    return unpadded_dc_text


def assym_decryption(c_text: bytes, private_key: bytes):
    '''
    Дешифрование текста асимметричным алгоритмом (RSA)

    Параметры:
        c_text (bytes): Зашифрованный текст в байтовом формате.
                        Получен в результате асимметричного шифрования с использованием OAEP.
                        Размер зависит от длины ключа (обычно 256, 384, 512 байт).

        private_key (bytes): Объект приватного RSA ключа.
                             Должен содержать закрытый ключ для расшифровки.
                             Поддерживает алгоритм OAEP с MGF1 и SHA-256.

    Возвращает:
        bytes: Дешифрованный текст (с добавленным padding'ом, требующим дальнейшей обработки)

    Примечание:
        - Используется OAEP padding с MGF1 (Mask Generation Function)
        - Хеш-алгоритм: SHA-256
        - Результат требует вызова dc_text_unpadding() для удаления padding'а
    '''
    dc_text = private_key.decrypt(c_text, assym_padding.OAEP(mgf=assym_padding.MGF1(
        algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    print('Assymetric decryption algorithm returned:')
    print(dc_text)
    return dc_text


def private_key_deserialize(filepath: str):
    private_bytes = fw.read_binary(filepath)
    d_public_key = load_pem_private_key(private_bytes, password=None)
    return d_public_key


def decryption(json_data):
    '''
    Непосредственно дешифрование
    '''
    # keys deserialization
    secret_key = fw.read_binary(json_data['secret_key'])
    private_key = private_key_deserialize(json_data['private_key'])

    # symmetric key decryption
    symm_key = assym_decryption(secret_key, private_key)
    print('Symmetric key decrypted:')
    print(symm_key)

    # text decryption
    c_text = fw.read_binary(json_data['encrypted_file'])
    dc_text = symm_text_decryption(c_text, symm_key)
    print("Successfully decrypted text:")
    print(dc_text)
    fw.write_text(json_data['decrypted_file'], dc_text)
