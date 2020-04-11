import time
import os
import json

def send_prompt(c):
    msg = '% '
    c.sendall(msg.encode('utf-8'))

class DB():
    def __init__(self):
        ## Data struct
        ## key: uname str unique
        ## value:
        ## {
        ##      email: str,
        ##      pwd:   str    
        ## }
        if os.path.isfile('NP_DB.json'):
            with open('NP_DB.json', 'r') as f:
                self.data = json.load(f)
        else:
            self.data = dict()

    def write(self, uname, email, pwd):
        if uname in self.data.keys():
            return -1
        else:
            self.data[uname] = {
                'email': email,
                'pwd': pwd
            }
            with open('NP_DB.json', 'w') as f:
                json.dump(self.data, f, indent=4)
            return 0
    
    def check_pwd(self, uname, pwd):
        if uname in self.data.keys():
            return self.data[uname]['pwd'] == pwd
        else:
            return False

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
    
    def remove(self, c_id):
        self.connection_list[c_id]['connection'].close()
        print('Connection leaved.')
        del self.connection_list[c_id]
    
    def login(self, c_id, uname):
        self.connection_list[c_id]['has_log_in'] = True
        self.connection_list[c_id]['uname'] = uname
    
    def logout(self, c_id):
        self.connection_list[c_id]['has_log_in'] = False
    
    def get_uname(self, c_id):
        return self.connection_list[c_id]['uname']

    def check_login(self, c_id):
        return self.connection_list[c_id]['has_log_in']