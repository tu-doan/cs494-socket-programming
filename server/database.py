""" Contain db connection and all functions """
import os
import psycopg2

try:
    conn = psycopg2.connect(
        dbname=os.getenv('DBNAME', 'postgres'),
        user=os.getenv('DBUSER', 'postgres'),
        host=os.getenv('DBHOST', 'localhost'),
        password=os.getenv('DBPASSWD', 'postgres')
    )
except:
    raise Exception("_ERROR_ Cannot connect to database.")

conn.autocommit = True


def test():
    """ Test connection """
    cur = conn.cursor()
    cur.execute("Select 1;")
    result = cur.fetchall()
    print("Connection successful to database." % result)
    cur.close()


def insert_user(username, password):
    """ Insert user """
    cur = conn.cursor()
    # check if username exist
    cur.execute("Select * from my_user where name='%s';" % username)
    result = cur.fetchall()
    if len(result) > 0:
        print("_ERROR_ Username '%s' exited!!!" % username)
        cur.close()
        return 0

    # Get max id
    cur.execute("Select max(id) from my_user;")
    result = cur.fetchall()
    uid = None
    if not result[0][0]:
        uid = 1
    else:
        uid = result[0][0] + 1
    cur.execute("""
        INSERT INTO my_user (id, name, password, date, note)
        VALUES (%s, '%s', '%s', '%s', '%s')
    """ % (uid, username, password, "01/01/1970", "Nothing to show."))
    cur.close()
    return uid


def login_user(username, password):
    """ Login user """
    cur = conn.cursor()
    # query with given username, password
    cur.execute(
        "Select * from my_user where name='%s' and password='%s';"
        % (username, password))
    result = cur.fetchall()
    if len(result) == 0:
        cur.close()
        return 0

    cur.close()
    return result[0][0]     # return id of user


def change_password(username, current_pass, new_pass):
    """ Login user """
    cur = conn.cursor()
    # query with given username, password
    cur.execute(
        "Select * from my_user where name='%s' and password='%s';"
        % (username, current_pass))
    result = cur.fetchall()
    if len(result) == 0:
        cur.close()
        return False

    cur.execute(
        "UPDATE my_user SET password='%s' WHERE name='%s';"
        % (new_pass, username))
    cur.close()
    return True


def get_user_info(user_id=None, username=None):
    """ Get user info by name or id. Only 1 of them should be used at a time.
    Example:
        get_user_info(username='tu')
        get_user_info(user_id=1)
    """
    cur = conn.cursor()
    # query with given username or id
    if username:
        cur.execute(
            "Select id, name, date, note from my_user where name='%s';"
            % (username))
    elif user_id:
        cur.execute(
            "Select id, name, date, note from my_user where id=%s;"
            % (user_id))
    else:
        raise Exception("Function requires at least one option: username or id")
    result = cur.fetchall()
    if len(result) == 0:
        return None
    cur.close()
    return result[0]


def update_user_info(user_id, field, new_value):
    """ Update user info by id
    Params:
        user_id: int
        field: string. Field you want to change value. Only accept 'date' and 'note'
        new_value: string/text. The new value will pass to selected field.
    Example:
        update_user_info(username='tu')
        update_user_info(id=1)
    """
    cur = conn.cursor()
    # query with given username or id
    field = field.lower()
    if field != "date" and field != "note":
        return False
    cur.execute(
        "UPDATE my_user SET %s='%s' WHERE id=%s;"
        % (field, new_value, user_id))
    cur.close()
    return True


print(get_user_info(user_id=1))
