from json import dumps, loads
from cryptography.fernet import Fernet


def make_msg(msg_type, data=None):
    """ Generate normal message to send """
    return dumps({'type': msg_type, 'data': data}).encode('utf-8')


def make_msg_encrypt(msg_type, data=None, key=None):
    """ Format of Sending message:
        {
            "type": string,
            "data": encrypted_data
        }
    """
    if not isinstance(data, dict):
        raise Exception("Data must be dict to be encrypted.")
    # Encrypt data only, not encrypt the type of message
    raw_data = dumps(data).encode('utf-8')
    _fernet = Fernet(key)
    encrypted = _fernet.encrypt(raw_data)
    encrypted_string = encrypted.decode('utf-8')
    return dumps({'type': msg_type, 'data': encrypted_string}).encode('utf-8')


def decode_msg(msg):
    """ Decode to get type and data of message """
    return loads(msg.decode('utf-8'))


def decrypt_data(encrypted_string, key):
    """ Decrypt the data of message """
    if not encrypted_string or not key:
        raise Exception('Missing argument.')
    _fernet = Fernet(key)
    decrypted = _fernet.decrypt(encrypted_string.encode('utf-8'))
    return loads(decrypted.decode('utf-8'))
