import utils
import sqlite3
import basic_func as bf
import board_post_func as bpf

class_mapping = {
    'register': bf.Register,
    'login': bf.Login,
    'logout': bf.Logout,
    'whoami': bf.WhoAmI,
    'exit': bf.Exit,
    'create-board': bpf.CreateBoard,
    'create-post': bpf.CreatePost,
    'list-board': bpf.ListBoard,
    'list-post': bpf.ListPost,
    'read': bpf.Read,
    'delete-post': bpf.DeletePost,
    'update-post': bpf.UpdatePost,
    'comment': bpf.Comment
}

def parse_client_signal(conn, Action):
    buf = conn.recv(2048)
    buf = buf.decode('utf-8').strip().split(' ')
    if buf[0] == 'True':
        flag, msg = Action.process()
    else:
        msg = "Receive client fail signal!\n"
    conn.sendall(msg.encode('utf-8'))

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
        try:
            utils.send_prompt(c)
            buf = c.recv(2048)
            buf = buf.decode('utf-8').strip().split(' ')
        except:
            connection.remove(c_id, db_conn)
            break

        cmd = buf[0]
        package = {
            'conn': c,
            'cursor': connection,
            'conn_id': c_id,
            'db_conn': db_conn,
            'db_cur': db_cur,
            'argv': buf[1:]
        }

        if cmd in class_mapping.keys():
            Action = class_mapping[cmd](package)
            flag, msg, add_list = Action.parse()
            msg = str(flag) + '$' + '$'.join(add_list) + ' ' + msg

            c.sendall(msg.encode('utf-8'))
            if cmd == 'exit':
                break
            if flag:
                parse_client_signal(c, Action)
        else:
            bf.Invalid(c, class_mapping.keys())