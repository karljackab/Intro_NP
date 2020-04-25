import sqlite3
import utils

def CreateBoard(c, connection, c_id, db_conn, db_cur, argv):
    if len(argv) != 1:
        msg = 'create-board <name>\n'
    elif not connection.check_login(c_id):
        msg = 'Please login first.\n'
    else:
        bname = argv[0]
        uname = connection.get_uname(c_id)
        try:
            db_cur.execute(f'''
                insert into board (bname, moderator) 
                values ("{bname}", "{uname}")
            ''')
            db_conn.commit()
            msg = 'Create board successfully.\n'
        except sqlite3.IntegrityError:
            msg = 'Board is already exist.\n'
    c.sendall(msg.encode('utf-8'))

def CreatePost(c, connection, c_id, db_conn, db_cur, argv):
    if len(argv) < 5:
        msg = 'create-post <board-name> --title <title> --content <content>\n'
    elif not connection.check_login(c_id):
        msg = 'Please login first.\n'
    else:
        bname = argv[0]
        uname = connection.get_uname(c_id)

        try:
            t_idx = argv.index('--title')
            c_idx = argv.index('--content')
        except:
            msg = 'create-post <board-name> --title <title> --content <content>\n'
            c.sendall(msg.encode('utf-8'))
            return

        if t_idx < c_idx:
            title = ' '.join(argv[t_idx+1:c_idx])
            content = ' '.join(argv[c_idx+1:]).replace('<br>','\n')
        else:
            title = ' '.join(argv[t_idx+1:])
            content = ' '.join(argv[c_idx+1:t_idx]).replace('<br>','\n')
        
        try:
            db_cur.execute(f'''
                insert into post (bname, title, author, content) 
                values ("{bname}", "{title}", "{uname}", "{content}")
            ''')
            db_conn.commit()
            msg = 'Create post successfully.\n'
        except sqlite3.IntegrityError:
            msg = 'Board does not exist.\n'
    c.sendall(msg.encode('utf-8'))

def ListBoard(c, db_cur, argv):
    if len(argv) > 1 or (len(argv) == 1 and argv[0][:2] != "##"):
        msg = 'list-board ##<key>\n'
    else:
        if len(argv) == 0:
            db_cur.execute(f'select * from board')
        else:
            keyword = argv[0][2:]
            db_cur.execute(f'select * from board where bname like "%{keyword}%"')
        res = db_cur.fetchall()
        msg = f"{'Index':10}{'Name':20}{'Moderator':20}\n"
        for idx, row in enumerate(res):
            msg += f'{idx+1:<10}{row[0]:20}{row[1]:20}\n'
    c.sendall(msg.encode('utf-8'))

def ListPost(c, db_cur, argv):
    if len(argv) == 0 or len(argv) > 2:
        msg = 'list-post <board-name> ##<key>\n'
    elif len(argv) == 2 and argv[1][:2] != '##':
        msg = 'list-post <board-name> ##<key>\n'
    else:
        db_cur.execute(f'select count(*) from board where bname="{argv[0]}"')
        cnt = db_cur.fetchone()[0]
        if cnt==0:
            msg = 'Board does not exist.\n'
        else:
            if len(argv) == 1:
                db_cur.execute(f'''
                    select pid, title, author, date_time
                    from post
                    where bname="{argv[0]}"
                ''')
            else:
                keyword = argv[1][2:]
                db_cur.execute(f'''
                    select pid, title, author, date_time
                    from post
                    where bname="{argv[0]}"
                    and title like "%{keyword}%"
                ''')
            res = db_cur.fetchall()

            msg = f"{'ID':10}{'Title':40}{'Author':20}{'Date':6}\n"
            for row in res:
                date = '/'.join(row[3].split(' ')[0].split('-')[1:])
                msg += f"{row[0]:<10}{row[1]:40}{row[2]:20}{date:6}\n"
    c.sendall(msg.encode('utf-8'))

def Read(c, db_cur, argv):
    if len(argv) != 1:
        msg = 'read <post-id>\n'
    else:
        pid = utils.check_pid(argv[0])
        if not pid:
            msg = 'Post does not exist.\n'
            c.sendall(msg.encode('utf-8'))
            return

        db_cur.execute(f'''
            select author, title, date_time, content
            from post
            where pid={pid}
        ''')
        res = db_cur.fetchone()
        if res is None:
            msg = 'Post does not exist.\n'
        else:
            msg = f"Author\t:{res[0]}\nTitle\t:{res[1]}\nDate\t:{res[2].split(' ')[0]}\n--\n{res[3]}\n--\n"
            db_cur.execute(f'''
                select author, content
                from comment
                where pid={pid}
                order by date(date_time) desc
            ''')
            res = db_cur.fetchall()
            for row in res:
                msg += f"{row[0]}: {row[1]}\n"

    c.sendall(msg.encode('utf-8'))

def DeletePost(c, connection, c_id, db_conn, db_cur, argv):
    if len(argv) != 1:
        msg = 'delete-post <post-id>\n'
    elif not connection.check_login(c_id):
        msg = 'Please login first.\n'
    else:
        pid = utils.check_pid(argv[0])
        if not pid:
            msg = 'Post does not exist.\n'
            c.sendall(msg.encode('utf-8'))
            return

        db_cur.execute(f'''
            select author
            from post
            where pid={argv[0]}
        ''')
        author = db_cur.fetchone()
        if author is None:
            msg = 'Post does not exist.\n'
        elif author[0] != connection.get_uname(c_id):
            msg = 'Not the post owner.\n'
        else:
            db_cur.execute(f'delete from post where pid={argv[0]}')
            db_conn.commit()
            msg = 'Delete successfully.\n'
    c.sendall(msg.encode('utf-8'))

def UpdatePost(c, connection, c_id, db_conn, db_cur, argv):
    if len(argv) < 3:
        msg = 'update-post <post-id> --title/content <new>\n'
    elif not connection.check_login(c_id):
        msg = 'Please login first.\n'
    else:
        pid = utils.check_pid(argv[0])
        if not pid:
            msg = 'Post does not exist.\n'
            c.sendall(msg.encode('utf-8'))
            return

        if argv[1] == '--title' or argv[1] == '--content':
            update_type = argv[1][2:]
            new_content = ' '.join(argv[2:]).replace('<br>','\n')

            db_cur.execute(f'''
                select author
                from post
                where pid={pid}
            ''')
            author = db_cur.fetchone()
            if author is None:
                msg = 'Post does not exist.\n'
            elif author[0] != connection.get_uname(c_id):
                msg = 'Not the post owner.\n'
            else:
                db_cur.execute(f'''
                    update post
                    set {update_type} = "{new_content}"
                    where pid={argv[0]}
                ''')
                db_conn.commit()
                msg = 'Update successfully.\n'
        else:
            msg = 'update-post <post-id> --title/content <new>\n'

    c.sendall(msg.encode('utf-8'))

def Comment(c, connection, c_id, db_conn, db_cur, argv):
    if len(argv) < 2:
        msg = 'comment <post-id> <comment>\n'
    elif not connection.check_login(c_id):
        msg = 'Please login first.\n'
    else:
        pid = utils.check_pid(argv[0])
        if not pid:
            msg = 'Post does not exist.\n'
            c.sendall(msg.encode('utf-8'))
            return

        db_cur.execute(f'''
            select count(*)
            from post
            where pid={pid}
        ''')
        cnt = db_cur.fetchone()[0]
        if cnt == 0:
            msg = 'Post does not exist.\n'
        else:
            uname = connection.get_uname(c_id)
            content = ' '.join(argv[1:])

            db_cur.execute(f'''
                insert into comment (author, content, pid)
                values ("{uname}", "{content}", "{pid}")
            ''')
            db_conn.commit()
            msg = 'Comment successfully.\n'
    c.sendall(msg.encode('utf-8'))