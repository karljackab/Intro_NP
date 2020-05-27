import sqlite3
import utils
import hashlib
import uuid

class Subscribe():
    def __init__(self, package):
        self.package = package

    def parse(self):
        sub_type = 'board/author'
        flag = False
        keyword, bname = '', ''
        try:
            cursor, conn_id, _, _, argv = utils.readPackage(self.package)
            if not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                if argv[0] == '--board':
                    sub_type = 'board'
                elif argv[0] == '--author':
                    sub_type = 'author'
                else:
                    msg = f'[Invalid option] subscribe --{sub_type} <{sub_type}-name> --keyword <keyword>\n'
                    sub_type = 'F'

                if sub_type != 'F':
                    k_idx = argv.index('--keyword')
                    bname = ' '.join(argv[1:k_idx])
                    keyword = " ".join(argv[k_idx+1:])

                    msg = '\n'
                    flag = True

        except Exception as e:
            print(e)
            msg = f'[Invalid option] subscribe --{sub_type} <{sub_type}-name> --keyword <keyword>\n'

        return flag, msg, [sub_type, keyword, bname]

class Unsubscribe():
    def __init__(self, package):
        self.package = package

    def parse(self):
        sub_type = 'board/author'
        flag = False
        bname_author = ''
        try:
            cursor, conn_id, _, _, argv = utils.readPackage(self.package)
            if not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                if argv[0] == '--board':
                    sub_type = 'board'
                elif argv[0] == '--author':
                    sub_type = 'author'
                else:
                    msg = f'unsubscribe --{sub_type} <{sub_type}-name>\n'
                    sub_type = 'F'

                if sub_type != 'F':
                    bname_author = ' '.join(argv[1:])
                    msg = '\n'
                    flag = True

        except Exception as e:
            print(e)
            msg = f'unsubscribe --{sub_type} <{sub_type}-name>\n'

        return flag, msg, [sub_type, bname_author]

class ListSub():
    def __init__(self, package):
        self.package = package
    
    def parse(self):
        flag = False
        try:
            cursor, conn_id, _, _, _ = utils.readPackage(self.package)
            if not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                msg = '\n'
                flag = True

        except Exception as e:
            print(e)
            msg = f'list-sub\n'

        return flag, msg, []
