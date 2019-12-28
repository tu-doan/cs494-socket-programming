

# Command and Message type
class Command:
    LOGIN = 'login'
    LOGIN_ENCRYPT = 'login -encrypt'

    REGISTER = 'register'
    REGISTER_ENCRYPT = 'register -encrypt'

    CHANGE_PASS = 'change_password'
    CHANGE_PASS_ENCRYPT = 'change_password -encrypt'

    CHECK_USER = 'check_user'
    CHECK_USER_ONL = 'check_user -online'
    CHECK_USER_DATE = 'check_user -date'
    CHECK_USER_NAME = 'check_user -name'
    CHECK_USER_NOTE = 'check_user -note'
    CHECK_USER_SHOW = 'check_user -show'

    SETUP_USER = 'setup_user'
    SETUP_USER_DATE = 'setup_user -date'
    SETUP_USER_NOTE = 'setup_user -note'

    UPLOAD = 'upload'
    UPLOAD_ENCRYPT = 'upload -encrypt'
    DOWNLOAD = 'download'
    DOWNLOAD_ENCRYPT = 'download -encrypt'

    CHAT = 'chat'
    CHAT_ENCRYPT = 'chat -encrypt'
