import argparse
import json

import modules_folder.key_generation as key_generation
import modules_folder.encryption as encryption
import modules_folder.decryption as decryption


def read_json():
    # читаем из файла
    with open('settings.json') as json_file:
        json_data = json.load(json_file)
    return json_data


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

    if args.generation:
        return 'generation'

    elif args.encryption:
        return 'encryption'

    elif args.decryption:
        return 'decryption'


if __name__ == '__main__':
    working_mode = argument_parsing()
    json_data = read_json()
    if working_mode == 'generation':
        key_generation.key_gen_and_save(json_data)
    elif working_mode == 'encryption':
        encryption.data_encryption(json_data)
    else:
        decryption.decryption(json_data)
