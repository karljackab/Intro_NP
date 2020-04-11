import utils

def main(connection, c_id, db):
    msg = '''********************************
** Welcome to the BBS server. **
********************************
'''
    c, _ = connection.get(c_id)
    c.sendall(msg.encode('utf-8'))    

    while True:
        utils.send_prompt(c)
        buf = c.recv(1024)
        try:
            buf = buf.decode('utf-8').strip().split(' ')
        except:
            connection.remove(c_id)
            break
        
        if buf[0] == 'register':
            Register(c, db, buf[1:])
        elif buf[0] == 'login':
            Login(connection, c_id, c, db, buf[1:])
        elif buf[0] == 'logout':
            if len(buf) != 1:
                msg = 'logout\n'
                c.sendall(msg.encode('utf-8'))
            else:
                Logout(connection, c_id, c)
        elif buf[0] == 'whoami':
            if len(buf) != 1:
                msg = 'whoami\n'
                c.sendall(msg.encode('utf-8'))
            else:
                WhoAmI(connection, c_id, c)
        elif buf[0] == 'exit':
            if len(buf) != 1:
                msg = 'exit\n'
                c.sendall(msg.encode('utf-8'))
            else:
                connection.remove(c_id)
                break
        else:
            Invalid(c)

def Invalid(c):
    msg = 'Available command: register, login, logout, whoami, exit\n'
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

def Login(connection, c_id, c, db, argv):
    if len(argv) != 2:
        msg = 'login <username> <password>\n'
    elif connection.check_login(c_id):
        msg = 'Please logout first.\n'
    else:
        uname, pwd = argv
        if not db.check_pwd(uname, pwd):
            msg = 'Login failed.\n'
        else:
            connection.login(c_id, uname)
            msg = f'Welcome, {uname}.\n'
    c.sendall(msg.encode('utf-8'))

def Register(c, db, argv):
    if len(argv) != 3:
        msg = 'Usage: register <username> <email> <password>\n'
    else:
        uname, email, pwd = argv
        if db.write(uname, email, pwd) != 0:
            msg = 'Username is already used.\n'
        else:
            msg = 'Register successfully.\n'
    c.sendall(msg.encode('utf-8'))