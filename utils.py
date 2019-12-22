from json import dumps, loads


def make_msg(msg_type, data=None):
    return dumps({'type': msg_type, 'data': data}).encode('utf-8')

def decode_msg(msg):
    return loads(msg.decode('utf-8'))
