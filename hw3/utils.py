import time
import os
import json

def send_prompt(c):
    msg = '% '
    c.sendall(msg.encode('utf-8'))

def readPackage(package):
    return package['cursor'], package['conn_id'], package['db_conn'], \
        package['db_cur'], package['argv']

class Connection():
    def __init__(self):
        self.connection_list = dict() #key: connection_id, value: connection_info

    def add(self, c, addr):
        c_id = f'{len(self.connection_list)}-{time.time()}'
        self.connection_list[c_id] = {
            'connection': c,
            'address': addr,
            'uname': '',
            'has_log_in': False,
        }
        print('New connection.')
        return c_id

    def get(self, c_id):
        return self.connection_list[c_id]['connection'], self.connection_list[c_id]['address']
    
    def remove(self, c_id, db_conn):
        self.connection_list[c_id]['connection'].close()
        print('Connection leaved.')
        del self.connection_list[c_id]

        if db_conn:
            db_conn.close()
    
    def login(self, c_id, uname):
        self.connection_list[c_id]['has_log_in'] = True
        self.connection_list[c_id]['uname'] = uname
    
    def logout(self, c_id):
        self.connection_list[c_id]['has_log_in'] = False
    
    def get_uname(self, c_id):
        return self.connection_list[c_id]['uname']

    def check_login(self, c_id):
        return self.connection_list[c_id]['has_log_in']