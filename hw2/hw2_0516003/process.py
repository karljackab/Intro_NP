import utils
import sqlite3
import basic_func as bf
import board_post_func as bpf

commands_list = [
    'register', 'login', 'logout', 'logout', 'whoami', 'exit', 'create-board', 
    'create-post', 'list-board', 'list-post', 'read', 'delete-post', 'update-post', 
    'comment'
]

def main(connection, c_id):
    msg = '''********************************
** Welcome to the BBS server. **
********************************
'''
    c, _ = connection.get(c_id)
    c.sendall(msg.encode('utf-8'))

    db_conn = sqlite3.connect('./NP_DB')
    db_cur = db_conn.cursor()

    db_cur.execute('PRAGMA foreign_keys = ON;') ## turn on foreign key

    while True:
        utils.send_prompt(c)
        buf = c.recv(2048)
        try:
            buf = buf.decode('utf-8').strip().split(' ')
        except:
            connection.remove(c_id, db_conn)
            break
        
        if buf[0] == 'register':
            bf.Register(c, db_conn, db_cur, buf[1:])
        elif buf[0] == 'login':
            bf.Login(c, connection, c_id, db_cur, buf[1:])
        elif buf[0] == 'logout':
            if len(buf) != 1:
                msg = 'logout\n'
                c.sendall(msg.encode('utf-8'))
            else:
                bf.Logout(connection, c_id, c)
        elif buf[0] == 'whoami':
            if len(buf) != 1:
                msg = 'whoami\n'
                c.sendall(msg.encode('utf-8'))
            else:
                bf.WhoAmI(connection, c_id, c)
        elif buf[0] == 'exit':
            if len(buf) != 1:
                msg = 'exit\n'
                c.sendall(msg.encode('utf-8'))
            else:
                connection.remove(c_id, db_conn)
                break
        elif buf[0] == 'create-board':
            bpf.CreateBoard(c, connection, c_id, db_conn, db_cur, buf[1:])
        elif buf[0] == 'create-post':
            bpf.CreatePost(c, connection, c_id, db_conn, db_cur, buf[1:])
        elif buf[0] == 'list-board':
            bpf.ListBoard(c, db_cur, buf[1:])
        elif buf[0] == 'list-post':
            bpf.ListPost(c, db_cur, buf[1:])
        elif buf[0] == 'read':
            bpf.Read(c, db_cur, buf[1:])
        elif buf[0] == 'delete-post':
            bpf.DeletePost(c, connection, c_id, db_conn, db_cur, buf[1:])
        elif buf[0] == 'update-post':
            bpf.UpdatePost(c, connection, c_id, db_conn, db_cur, buf[1:])
        elif buf[0] == 'comment':
            bpf.Comment(c, connection, c_id, db_conn, db_cur, buf[1:])
        else:
            bf.Invalid(c, commands_list)

