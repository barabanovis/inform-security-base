from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

import os  # можно обойтись стандартным модулем


def symmetric_key_generate() -> str:
    # генерация ключа симметричного алгоритма шифрования
    key = os.urandom(32)  # это байты
    print("Symmetric key generated!")
    print("Type of key: ", type(key))
    print("Key:", key)
    return key


def asymmetric_key_generate():
    # генерация пары ключей для асимметричного алгоритма шифрования
    keys = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    private_key = keys
    public_key = keys.public_key()

    print("private key type:", type(private_key))
    print("private key:", private_key)
    print("public key type:", type(public_key))
    print("private key:", public_key)
    return [private_key, public_key]


def text_key_serialize(filepath: str, key: str) -> None:
    with open(filepath, 'wb') as key_file:
        key_file.write(key)


def public_key_serialize(public_pem_path: str, public_key):
    # сериализация открытого ключа в файл
    with open(public_pem_path, 'wb') as public_out:
        public_out.write(public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                 format=serialization.PublicFormat.SubjectPublicKeyInfo))


def private_key_serialize(private_pem_path: str, private_key):
    # сериализация закрытого ключа в файл
    with open(private_pem_path, 'wb') as private_out:
        private_out.write(private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                                                    encryption_algorithm=serialization.NoEncryption()))


def RSA_encryption(text: str, public_key):
    # шифрование текста при помощи RSA-OAEP (это усиливающая классический RSA cхема с использованием двух криптостойких хеш-функций и паддинга, если интересно, можно почитать здесь https://habr.com/ru/post/99376/)
    text = bytes(text)
    c_text = public_key.encrypt(text, padding.OAEP(mgf=padding.MGF1(
        algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

    print("RSA encryption successful!")
    return c_text


def key_gen_and_save(json_data):
    # symmetric key gen and save
    symm_key = symmetric_key_generate()
    text_key_serialize(json_data['symmetric_key'], symm_key)

    # asymm keys gen and save
    private_key, public_key = asymmetric_key_generate()
    public_key_serialize(json_data['public_key'], public_key)
    private_key_serialize(json_data['private_key'], private_key)

    # encryption of symm_key
    crypted_symm_key = RSA_encryption(symm_key, public_key)
    text_key_serialize(json_data['secret_key'], crypted_symm_key)
