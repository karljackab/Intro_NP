import sqlite3

def Invalid(c, commands_list):
    msg = 'Available command: '
    for command in commands_list[:-1]:
        msg += command + ', '
    msg += commands_list[-1] + '\n'
    c.sendall(msg.encode('utf-8'))

def WhoAmI(connection, c_id, c):
    if not connection.check_login(c_id):
        msg = 'Please login first.\n'
    else:
        uname = connection.get_uname(c_id)
        msg = f'{uname}\n'
    c.sendall(msg.encode('utf-8'))

def Logout(connection, c_id, c):
    if not connection.check_login(c_id):
        msg = 'Please login first.\n'
    else:
        uname = connection.get_uname(c_id)
        connection.logout(c_id)
        msg = f'Bye, {uname}.\n'
    c.sendall(msg.encode('utf-8'))

def Login(c, connection, c_id, db_cur, argv):
    if len(argv) != 2:
        msg = 'login <username> <password>\n'
    elif connection.check_login(c_id):
        msg = 'Please logout first.\n'
    else:
        uname, pwd = argv
        db_cur.execute(f'select count(*) from user where uname = "{uname}" and pwd = "{pwd}"')
        res = db_cur.fetchone()[0]
        
        if res == 0:
            msg = 'Login failed.\n'
        else:
            connection.login(c_id, uname)
            msg = f'Welcome, {uname}.\n'
    c.sendall(msg.encode('utf-8'))

def Register(c, db_conn, db_cur, argv):
    if len(argv) != 3:
        msg = 'Usage: register <username> <email> <password>\n'
    else:
        uname, email, pwd = argv
        try:
            db_cur.execute(f'insert into user (uname, email, pwd) values ("{uname}", "{email}", "{pwd}")')
            db_conn.commit()
            msg = 'Register successfully.\n'
        except sqlite3.IntegrityError:
            msg = 'Username is already used.\n'
    c.sendall(msg.encode('utf-8'))