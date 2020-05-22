import sqlite3
import utils
import hashlib

def Invalid(conn, commands_list):
    msg = 'False|Available command: ' + ', '.join(commands_list) + '\n'
    conn.sendall(msg.encode('utf-8'))

class Exit():
    def __init__(self, package):
        self.package = package
    def parse(self):
        try:
            cursor, conn_id, db_conn, _, argv = utils.readPackage(self.package)
            if len(argv) != 0:
                msg = 'exit\n'
            else:
                msg = '\n'
                cursor.remove(conn_id, db_conn)
            
        except Exception as e:
            # print(e)
            msg = 'exit ERROR!\n'

        return False, msg, []

class WhoAmI():
    def __init__(self, package):
        self.package = package
    def parse(self):
        try:
            cursor, conn_id, _, _, argv = utils.readPackage(self.package)
            if len(argv) != 0:
                msg = 'whoami\n'
            elif not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                uname = cursor.get_uname(conn_id)
                msg = f'{uname}\n'
            
        except Exception as e:
            # print(e)
            msg = 'whoami ERROR!\n'

        return False, msg, []

class Logout():
    def __init__(self, package):
        self.package = package

    def parse(self):
        flag = False
        try:
            cursor, conn_id, _, _, argv = utils.readPackage(self.package)
            if len(argv) != 0:
                msg = 'logout\n'
            elif not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                flag = True
                msg = f'\n'
            
        except Exception as e:
            # print(e)
            msg = 'logout ERROR!\n'

        return flag, msg, []
    
    def process(self):
        try:
            cursor, conn_id, _, _, _ = utils.readPackage(self.package)
            uname = cursor.get_uname(conn_id)
            cursor.logout(conn_id)
            msg = f'Bye, {uname}.\n'
        except Exception as e:
            # print(e)
            msg = 'logout ERROR!\n'
        
        return msg

class Login():
    def __init__(self, package):
        self.package = package

    def parse(self):
        flag = False
        bucket_name = ''
        try:
            cursor, conn_id, _, db_cur, argv = utils.readPackage(self.package)
            if cursor.check_login(conn_id):
                msg = 'Please logout first.\n'
            else:
                uname, pwd = argv
                db_cur.execute(f'select bucket_name from user where uname = "{uname}" and pwd = "{pwd}"')
                bucket_name = db_cur.fetchone()
                if bucket_name is None:
                    bucket_name = 'ERROR'
                    msg = 'Login failed.\n'
                else:
                    bucket_name = bucket_name[0]
                    flag = True
                    msg = '\n'
        except Exception as e:
            # print(e)
            msg = msg = 'login <username> <password>\n'

        return flag, msg, [bucket_name]
    
    def process(self):
        try:
            cursor, conn_id, _, _, argv = utils.readPackage(self.package)
            uname = argv[0]
            cursor.login(conn_id, uname)
            msg = f'Welcome, {uname}.\n'
        except Exception as e:
            # print(e)
            msg = 'Usage: register <username> <email> <password>\n'
        
        return msg

class Register():
    def __init__(self, package):
        self.package = package
        self.md5 = hashlib.md5()

    def parse(self):
        flag = False
        bucket_name = ''
        try:
            _, _, _, db_cur, argv = utils.readPackage(self.package)
            uname, email, pwd = argv
            db_cur.execute(f'select count(*) from user where uname = "{uname}"')
            res = db_cur.fetchone()[0]
            if res == 0:
                msg = "\n"
                flag = True
                self.md5.update(f'{res}{email}{pwd}'.encode('utf-8'))
                bucket_name = '0516003-'+uname.lower()+'-'+self.md5.hexdigest()

                self.package['argv'].append(bucket_name)
            else:
                msg = "Username is already used.\n"
        except Exception as e:
            # print(e)
            msg = 'Usage: register <username> <email> <password>\n'

        return flag, msg, [bucket_name]

    def process(self):
        try:
            _, _, db_conn, db_cur, argv = utils.readPackage(self.package)
            uname, email, pwd, bucket_name = argv
            db_cur.execute(f'insert into user (uname, bucket_name, email, pwd) values ("{uname}", "{bucket_name}", "{email}", "{pwd}")')
            db_conn.commit()
            msg = 'Register successfully.\n'
        except:
            msg = 'Usage: register <username> <email> <password>\n'
        
        return msg