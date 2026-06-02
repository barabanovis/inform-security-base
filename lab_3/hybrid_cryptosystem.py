import argparse

from modules_folder.key_generation import key_gen_and_save
from modules_folder.encryption import data_encryption
from modules_folder.decryption import decryption

from modules_folder.fileworking import read_json


def argument_parsing() -> str:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-gen', '--generation',
                       action='store_true',
                       help='Запускает режим генерации ключей')
    group.add_argument('-enc', '--encryption',
                       action='store_true',
                       help='Запускает режим шифрования')
    group.add_argument('-dec', '--decryption',
                       action='store_true',
                       help='Запускает режим дешифрования')

    args = parser.parse_args()

    match args:
        case _ if args.generation:
            return 'generation'
        case _ if args.encryption:
            return 'encryption'
        case _ if args.decryption:
            return 'decryption'


if __name__ == '__main__':
    working_mode = argument_parsing()
    json_data = read_json()
    match working_mode:
        case 'generation':
            key_gen_and_save(json_data)
        case  'encryption':
            data_encryption(json_data)
        case 'decryption':
            decryption(json_data)
