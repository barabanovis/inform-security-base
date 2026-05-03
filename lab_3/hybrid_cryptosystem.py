import argparse
import json

import modules_folder.key_generation as key_generation
import modules_folder.encryption as encryption
import modules_folder.decryption as decryption

settings = {
    'initial_file': 'data/initial_text.txt',
    'encrypted_file': 'data/encrypted_text.txt',
    'decrypted_file': 'data/dectypted_text.txt',
    'symmetric_key': 'data/symmetric_key.txt',
    'public_key': 'data/public_key.pem',
    'private_key': 'data/private_key.pem',
    'secret_key': 'data/secret_key.pem',
}

# пишем в файл
with open('settings.json', 'w') as fp:
    json.dump(settings, fp)


def argument_parsing():
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

    # читаем из файла
    with open('settings.json') as json_file:
        json_data = json.load(json_file)

    if args.generation:
        key_generation.key_gen_and_save(json_data)
    elif args.encryption:
        encryption.data_encryption(json_data)
    elif args.decryption:
        # дешифруем
        pass


if __name__ == '__main__':
    argument_parsing()
