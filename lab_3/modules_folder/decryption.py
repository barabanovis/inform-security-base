import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
# импорт RSA и padding для асимметричных алгоритмов
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asymmetric_padding
# для загрузки/сохранения ключей
from cryptography.hazmat.primitives import serialization


def symm_text_decryption(c_text: bytes, symm_key: bytes) -> str:
    """
    Дешифрование и депадинг текста симметричным алгоритмом (3DES-CBC + PKCS7).

    Args:
        c_text (bytes): зашифрованные данные (IV + ciphertext)
        symm_key (bytes): ключ 3DES (16 или 24 байта)

    Returns:
        str: расшифрованный текст в виде строки
    """
    try:
        # Проверка длины ключа для 3DES
        if len(symm_key) not in (16, 24):
            raise ValueError("3DES key must be 16 or 24 bytes long")

        # Извлекаем IV (первые 8 байт) и зашифрованные данные
        iv = c_text[:8]
        encrypted_data = c_text[8:]

        # Создаём шифр для дешифрования
        cipher = Cipher(
            algorithms.TripleDES(symm_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # Дешифрование
        padded_text = decryptor.update(encrypted_data) + decryptor.finalize()

        # Депадинг (удаление PKCS7 дополнения)
        # 64 бита = 8 байт (размер блока 3DES)
        unpadder = padding.PKCS7(64).unpadder()
        dc_text_bytes = unpadder.update(padded_text) + unpadder.finalize()

        # Преобразование bytes в str
        dc_text = dc_text_bytes.decode('utf-8')

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


def assym_decryption(c_text: bytes, private_key):
    # дешифрование текста асимметричным алгоритмом
    dc_text = private_key.decrypt(c_text, padding.OAEP(mgf=padding.MGF1(
        algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    print("Assym_decryption: ", dc_text)
    return dc_text
