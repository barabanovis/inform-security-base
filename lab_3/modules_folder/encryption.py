from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding as asymm_padding
from cryptography.hazmat.primitives import padding as symm_padding
from cryptography.hazmat.primitives import hashes
import os


def symm_key_deserialize(symm_key_path: str):
    # десериализация ключа симметричного алгоритма
    with open(symm_key_path, mode='rb') as key_file:
        content = key_file.read()

    print("Deserialized symm key type:", type(content))
    print("Deserialized symm key:", content)
    return content


def RSA_decrypt(c_text: bytes, private_key):
    # дешифрование текста асимметричным алгоритмом
    dc_text = private_key.decrypt(c_text, asymm_padding.OAEP(mgf=asymm_padding.MGF1(
        algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

    print("Text decrypted!")
    print("Text: ", dc_text)
    return dc_text


def private_key_deserialize(private_pem: str):
    # десериализация закрытого ключа
    with open(private_pem, 'rb') as pem_in:
        private_bytes = pem_in.read()
    d_private_key = load_pem_private_key(private_bytes, password=None)

    print(type(d_private_key))
    print(d_private_key)
    return d_private_key


def read_text(textfile_path: str):
    with open(textfile_path, 'r') as textfile:
        text = textfile.read()
    return text


def text_padding(text: str) -> bytes:
    print("=== DEBUG: Padding Process ===")
    print(f"Input text (str): {text}")

    # Конвертируем в байты
    text_bytes = text.encode('UTF-8')
    print(f"Text as bytes: {text_bytes}")
    print(f"Initial length: {len(text_bytes)} bytes")

    # Создаём паддер
    padder = padding.ANSIX923(16).padder()

    # Применяем дополнение
    padded_text = padder.update(text_bytes) + padder.finalize()

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


def symm_encryption(symm_key: bytes, padded_text: bytes):
    # шифрование текста симметричным алгоритмом
    # случайное значение для инициализации блочного режима, должно быть размером с блок и каждый раз новым
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(symm_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    c_text = encryptor.update(padded_text) + encryptor.finalize()

    print("Text successfully encrypted using a symmetric key!")
    print("TEXT: ", padded_text)


# Сохранить текст по указанному пути
def save_text(text: str, save_path: str):
    with open(save_path, 'w') as save_file:
        save_file.write(text)
    print("Text saved successfully!")


def data_encryption(json_data):
    text_padding("my text")

    symm_key_crypted = symm_key_deserialize(json_data['secret_key'])
    private_key = private_key_deserialize(json_data['private_key'])
    symm_key = RSA_decrypt(symm_key_crypted, private_key)
    text = read_text(json_data['initial_file'])
    text = text_padding(text)
    c_text = symm_encryption(symm_key, text)
    save_text(c_text, json_data['encrypted_file'])
