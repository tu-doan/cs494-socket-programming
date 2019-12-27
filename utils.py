from json import dumps, loads
from cryptography.fernet import Fernet


def make_msg(msg_type, data=None):
    return dumps({'type': msg_type, 'data': data}).encode('utf-8')


def make_msg_encrypt(msg_type, data=None, key=None):
    if not isinstance(data, dict):
        raise Exception("Data must be dict to be encrypted.")
    raw_data = dumps(data).encode('utf-8')
    _fernet = Fernet(key)
    encrypted = _fernet.encrypt(raw_data)
    encrypted_string = encrypted.decode('utf-8')

    # try decrypt
    print(decrypt_data(encrypted_string, key))
    return dumps({'type': msg_type, 'data': encrypted_string}).encode('utf-8')


def decode_msg(msg):
    return loads(msg.decode('utf-8'))


def decrypt_data(encrypted_string, key):
    if not encrypted_string or not key:
        raise Exception('Missing argument.')
    _fernet = Fernet(key)
    decrypted = _fernet.decrypt(encrypted_string.encode('utf-8'))
    return loads(decrypted.decode('utf-8'))
