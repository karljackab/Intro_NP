import sqlite3
import utils
import hashlib

def Invalid(conn, commands_list):
    msg = 'Available command: ' + ', '.join(commands_list) + '\n'
    conn.sendall(msg.encode('utf-8'))

def Exit(package):
    conn = package['conn']
    cursor, conn_id, db_conn, _, argv = utils.readPackage(package)

    if len(argv) != 0:
        msg = 'exit\n'
        conn.sendall(msg.encode('utf-8'))
        return

    try:
        cursor.remove(conn_id, db_conn)
    except:
        msg = 'exit ERROR!\n'
        conn.sendall(msg.encode('utf-8'))

def WhoAmI(package):
    conn = package['conn']
    cursor, conn_id, _, _, argv = utils.readPackage(package)

    if len(argv) != 0:
        msg = 'whoami\n'
        conn.sendall(msg.encode('utf-8'))
        return

    try:
        if not cursor.check_login(conn_id):
            msg = 'Please login first.\n'
        else:
            uname = cursor.get_uname(conn_id)
            msg = f'{uname}\n'
    except:
        msg = 'whoami ERROR!\n'

    conn.sendall(msg.encode('utf-8'))

def Logout(package):
    conn = package['conn']
    cursor, conn_id, _, _, argv = utils.readPackage(package)

    if len(argv) != 0:
        msg = 'logout\n'
        conn.sendall(msg.encode('utf-8'))
        return
    
    try:
        if not cursor.check_login(conn_id):
            msg = 'Please login first.\n'
        else:
            uname = cursor.get_uname(conn_id)
            cursor.logout(conn_id)
            msg = f'Bye, {uname}.\n'
    except:
        msg = 'logout ERROR!\n'
        
    conn.sendall(msg.encode('utf-8'))

def Login(package):
    try:
        conn = package['conn']
        cursor, conn_id, _, db_cur, argv = utils.readPackage(package)
        if cursor.check_login(conn_id):
            msg = 'Please logout first.\n'
        else:
            uname, pwd = argv
            db_cur.execute(f'select count(*) from user where uname = "{uname}" and pwd = "{pwd}"')
            res = db_cur.fetchone()[0]
            
            if res == 0:
                msg = 'Login failed.\n'
            else:
                cursor.login(conn_id, uname)
                msg = f'Welcome, {uname}.\n'
    except:
        msg = 'login <username> <password>\n'

    conn.sendall(msg.encode('utf-8'))


class Register():
    def __init__(self, package):
        self.package = package
        self.md5 = hashlib.md5()

    def parse(self):
        flag = False
        bucket_name = ''
        try:
            # conn = package['conn']
            _, _, _, db_cur, argv = utils.readPackage(self.package)
            uname, email, pwd = argv
            db_cur.execute(f'select count(*) from user where uname = "{uname}"')
            res = db_cur.fetchone()[0]
            if res == 0:
                msg = "\n"
                flag = True
                self.md5.update(f'{res}{email}{pwd}'.encode('utf-8'))
                bucket_name = self.md5.hexdigest()

                self.package['argv'].append(bucket_name)
            else:
                msg = "Username is already used.\n"
        except Exception as e:
            print(e)
            msg = 'Usage: register <username> <email> <password>\n'

        return flag, msg, [bucket_name]

    def process(self):
        flag = False
        try:
            _, _, db_conn, db_cur, argv = utils.readPackage(self.package)
            uname, email, pwd, bucket_name = argv
            db_cur.execute(f'insert into user (uname, bucket_name, email, pwd) values ("{uname}", "{bucket_name}", "{email}", "{pwd}")')
            db_conn.commit()
            msg = 'Register successfully.\n'
            flag = True
        except:
            msg = 'Usage: register <username> <email> <password>\n'
        
        return flag, msg

# def parseRegister(package):
#     try:
#         conn = package['conn']
#         _, _, _, db_cur, argv = utils.readPackage(package)
#         uname, _, _ = argv
#         db_cur.execute(f'select count(*) from user where uname = "{uname}"')
#         res = db_cur.fetchone()[0]
#         if res == 0:
#             msg = "True\n"
#         else:
#             msg = "False Username is already used.\n"
#     except:
#         msg = 'False Usage: register <username> <email> <password>\n'

#     conn.sendall(msg.encode('utf-8'))

# def Register(package):
#     try:
#         conn = package['conn']
#         _, _, db_conn, db_cur, argv = utils.readPackage(package)
#         uname, email, pwd = argv
#         try:
#             db_cur.execute(f'insert into user (uname, email, pwd) values ("{uname}", "{email}", "{pwd}")')
#             db_conn.commit()
#             msg = 'Register successfully.\n'
#         except sqlite3.IntegrityError:
#             msg = 'Username is already used.\n'
#     except:
#         msg = 'Usage: register <username> <email> <password>\n'

#     conn.sendall(msg.encode('utf-8'))
