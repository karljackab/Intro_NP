import sqlite3
import utils
import hashlib
import uuid

class CreateBoard():
    def __init__(self, package):
        self.package = package
    def parse(self):
        try:
            cursor, conn_id, db_conn, db_cur, argv = utils.readPackage(self.package)
            if not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                bname = argv[0]
                uname = cursor.get_uname(conn_id)
                try:
                    db_cur.execute(f'''
                        insert into board (bname, moderator) 
                        values ("{bname}", "{uname}")
                    ''')
                    db_conn.commit()
                    msg = 'Create board successfully.\n'
                except sqlite3.IntegrityError:
                    msg = 'Board already exist.\n'
            
        except Exception as e:
            # print(e)
            msg = 'create-board <name>\n'

        return False, msg, []

class CreatePost():
    def __init__(self, package):
        self.package = package
        self.md5 = hashlib.md5()

    def parse(self):
        flag = False
        upload_file_name, uname, bname = '', '', ''
        try:
            cursor, conn_id, _, db_cur, argv = utils.readPackage(self.package)
            if len(argv) < 5:
                msg = 'create-post <board-name> --title <title> --content <content>\n'
            elif not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                bname, uname = argv[0], cursor.get_uname(conn_id)
                _, _ = argv.index('--title'), argv.index('--content')

                db_cur.execute(f'select count(*) from board where bname = "{bname}"')
                res = db_cur.fetchone()[0]
                if res == 0:
                    msg = 'Board does not exist.\n'
                else:
                    flag, msg = True, '\n'
                    upload_file_name = 'post_'+uuid.uuid4().hex
                    self.package['argv'].append(upload_file_name)

        except Exception as e:
            # print(e)
            msg = 'create-post <board-name> --title <title> --content <content>\n'

        return flag, msg, [upload_file_name, uname, bname]

    def process(self):
        try:
            cursor, conn_id, db_conn, db_cur, argv = utils.readPackage(self.package)
            bname, uname = argv[0], cursor.get_uname(conn_id)
            upload_file_name = argv[-1]

            t_idx = argv.index('--title')
            c_idx = argv.index('--content')

            if t_idx < c_idx:
                title = ' '.join(argv[t_idx+1:c_idx])
            else:
                title = ' '.join(argv[t_idx+1:])

            db_cur.execute(f'''
                insert into post (bname, title, author, upload_file_name) 
                values ("{bname}", "{title}", "{uname}", "{upload_file_name}")
            ''')
            db_conn.commit()
            msg = 'Create post successfully.\n'

        except Exception as e:
            print(e)
            msg = 'create-post <board-name> --title <title> --content <content>\n'

        return msg

class ListBoard():
    def __init__(self, package):
        self.package = package
    def parse(self):
        try:
            _, _, _, db_cur, argv = utils.readPackage(self.package)
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
        except Exception as e:
            # print(e)
            msg = 'list-board ##<key>\n'

        return False, msg, []

class ListPost():
    def __init__(self, package):
        self.package = package
    def parse(self):
        try:
            _, _, _, db_cur, argv = utils.readPackage(self.package)
            if len(argv) == 0 or len(argv) > 2 or (len(argv) == 2 and argv[1][:2] != '##'):
                msg = 'list-post <board-name> ##<key>\n'
            else:
                bname = argv[0]
                db_cur.execute(f'select count(*) from board where bname="{bname}"')
                cnt = db_cur.fetchone()[0]

                if cnt==0:
                    msg = 'Board does not exist.\n'
                else:
                    if len(argv) == 1:
                        db_cur.execute(f'''
                            select pid, title, author, date_time
                            from post
                            where bname="{bname}"
                        ''')
                    else:
                        keyword = argv[1][2:]
                        db_cur.execute(f'''
                            select pid, title, author, date_time
                            from post
                            where bname="{bname}"
                            and title like "%{keyword}%"
                        ''')
                    res = db_cur.fetchall()

                    msg = f"{'ID':10}{'Title':40}{'Author':20}{'Date':6}\n"
                    for row in res:
                        date = '/'.join(row[3].split(' ')[0].split('-')[1:])
                        msg += f"{row[0]:<10}{row[1]:40}{row[2]:20}{date:6}\n"
        except Exception as e:
            # print(e)
            msg = 'list-post <board-name> [##<key>]\n'

        return False, msg, []

class Read():
    def __init__(self, package):
        self.package = package
    def parse(self):
        flag, addi_list = False, []
        try:
            _, _, _, db_cur, argv = utils.readPackage(self.package)
            if len(argv) != 1:
                msg = 'read <post-id>\n'
            else:
                pid = int(argv[0])

                db_cur.execute(f'''
                    select p.author, p.title, p.date_time, p.upload_file_name, u.bucket_name
                    from post as p, user as u
                    where p.pid={pid}
                    and p.author = u.uname
                ''')
                data = db_cur.fetchone()

                if data is None:
                    msg = 'Post does not exist.\n'
                else:
                    author, title, date_time, upload_file_name, bucket_name = data
                    addi_list.extend([author, title, date_time, upload_file_name, bucket_name])
                    db_cur.execute(f'''
                        select author, upload_comment_name
                        from comment
                        where pid={pid}
                        order by date(date_time) desc
                    ''')
                    res = db_cur.fetchall()
                    for row in res:
                        addi_list.append(row[0])
                        addi_list.append(row[1])
                    msg = '\n'
                    flag = True
        except Exception as e:
            # print(e)
            msg = 'read <post-id>\n'

        return flag, msg, addi_list

class DeletePost():
    def __init__(self, package):
        self.package = package
    def parse(self):
        flag, addi_list = False, []
        try:
            cursor, conn_id, _, db_cur, argv = utils.readPackage(self.package)
            if len(argv) != 1:
                msg = 'delete-post <post-id>\n'
            elif not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                pid = int(argv[0])
                db_cur.execute(f'''
                    select p.author, u.bucket_name, p.upload_file_name
                    from post as p, user as u
                    where p.pid={pid}
                    and p.author = u.uname
                ''')
                data = db_cur.fetchone()
                if data is None:
                    msg = 'Post does not exist.\n'
                elif data[0] != cursor.get_uname(conn_id):
                    msg = 'Not the post owner.\n'
                else:
                    addi_list.extend([data[1], data[2]])
                    db_cur.execute(f'''
                        select upload_comment_name
                        from comment
                        where pid={pid}
                    ''')
                    data = db_cur.fetchall()
                    for row in data:
                        addi_list.append(row[0])
                    flag = True
                    msg = '\n'
        except ValueError:
            msg = 'Post does not exist.\n'
        except:
            msg = 'delete-post <post-id>\n'

        return flag, msg, addi_list

    def process(self):
        try:
            _, _, db_conn, db_cur, argv = utils.readPackage(self.package)
            pid = int(argv[0])
            db_cur.execute(f'delete from post where pid={pid}')
            db_conn.commit()
            msg = 'Delete successfully.\n'
        except ValueError:
            msg = 'Post does not exist.\n'
        except:
            msg = 'delete-post <post-id>\n'

        return msg

class UpdatePost():
    def __init__(self, package):
        self.package = package
    def parse(self):
        flag, addi_list = False, []
        try:
            cursor, conn_id, db_conn, db_cur, argv = utils.readPackage(self.package)
            if not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                pid = int(argv[0])

                if argv[1] == '--title' or argv[1] == '--content':
                    update_type = argv[1][2:]
                    new_content = ' '.join(argv[2:])
                    db_cur.execute(f'''
                        select p.author, u.bucket_name, p.upload_file_name
                        from post as p, user as u
                        where p.pid={pid}
                        and u.uname=p.author
                    ''')
                    data = db_cur.fetchone()
                    if data is None:
                        msg = 'Post does not exist.\n'
                    elif data[0] != cursor.get_uname(conn_id):
                        msg = 'Not the post owner.\n'
                    else:
                        if argv[1] == '--content':
                            bucket_name, upload_file_name = data[1], data[2]
                            addi_list.extend([bucket_name, upload_file_name, new_content])
                            flag = True
                            msg = '\n'
                        else:
                            db_cur.execute(f'''
                                update post
                                set {update_type} = "{new_content}"
                                where pid={pid}
                            ''')
                            db_conn.commit()
                            msg = 'Update successfully.\n'
                else:
                    msg = 'update-post <post-id> --title/content <new>\n'
        except ValueError:
            msg = 'Post does not exist.\n'
        except Exception as e:
            # print(e)
            msg = 'update-post <post-id> --title/content <new>\n'

        return flag, msg, addi_list

class Comment():
    def __init__(self, package):
        self.package = package
    def parse(self):
        flag = False
        bucket_name, upload_comment_name = '', ''
        try:
            cursor, conn_id, _, db_cur, argv = utils.readPackage(self.package)
            if not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                pid = int(argv[0])

                db_cur.execute(f'''
                    select u.bucket_name
                    from post as p, user as u
                    where p.pid={pid}
                    and p.author = u.uname
                ''')
                data = db_cur.fetchone()
                if data is None:
                    msg = 'Post does not exist.\n'
                else:
                    try:
                        bucket_name = data[0]
                        upload_comment_name = 'comment_'+uuid.uuid4().hex
                        self.package['argv'].append(upload_comment_name)
                        flag = True
                        msg = '\n'
                    except Exception as e:
                        # print(e)
                        msg = 'Post does not exist.\n'
        except ValueError as e:
            msg = 'Post does not exist.\n'
        except Exception as e:
            # print(e)
            msg = 'comment <post-id> <comment>\n'

        return flag, msg, [bucket_name, upload_comment_name]
    
    def process(self):
        try:
            cursor, conn_id, db_conn, db_cur, argv = utils.readPackage(self.package)
            pid = int(argv[0])
            upload_comment_name = self.package['argv'][-1]
            try:
                uname = cursor.get_uname(conn_id)
                db_cur.execute(f'''
                    insert into comment (author, upload_comment_name, pid)
                    values ("{uname}", "{upload_comment_name}", "{pid}")
                ''')
                db_conn.commit()
                msg = 'Comment successfully.\n'
            except Exception as e:
                # print(e)
                msg = 'Post does not exist.\n'
        except Exception as e:
            # print(e)
            msg = 'comment <post-id> <comment>\n'

        return msg