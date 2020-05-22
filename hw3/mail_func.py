import sqlite3
import utils
import hashlib
import uuid

class MailTo():
    def __init__(self, package):
        self.package = package
    def parse(self):
        flag = False
        addi_list = []
        try:
            cursor, conn_id, _, db_cur, argv = utils.readPackage(self.package)
            if not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                # to_user_name = argv[0]
                s_idx, c_idx = argv.index('--subject'), argv.index('--content')
                dash_idx = min(s_idx, c_idx)
                to_user_name = ' '.join(argv[:dash_idx])

                db_cur.execute(f'select bucket_name from user where uname = "{to_user_name}"')
                data = db_cur.fetchone()

                if data is None:
                    msg = f'{to_user_name} does not exist.\n'
                else:
                    addi_list.append(data[0])
                    upload_mail_name = 'mail_'+uuid.uuid4().hex
                    addi_list.append(upload_mail_name)
                    flag, msg = True, '\n'
                    self.package['argv'].append(upload_mail_name)

        except Exception as e:
            # print(e)
            msg = 'mail-to <username> --subject <subject> --content <content>\n'
        
        return flag, msg, addi_list
    
    def process(self):
        try:
            cursor, conn_id, db_conn, db_cur, argv = utils.readPackage(self.package)
            to_user_name, uname = argv[0], cursor.get_uname(conn_id)
            upload_mail_name = argv[-1]

            s_idx = argv.index('--subject')
            c_idx = argv.index('--content')

            if s_idx < c_idx:
                subject = ' '.join(argv[s_idx+1:c_idx])
            else:
                subject = ' '.join(argv[s_idx+1:])

            db_cur.execute(f'''
                insert into mail (mail_subject, source_user, target_user, upload_mail_name) 
                values ("{subject}", "{uname}", "{to_user_name}", "{upload_mail_name}")
            ''')
            db_conn.commit()
            msg = 'Sent successfully.\n'
        except Exception as e:
            # print(e)
            msg = 'mail-to <username> --subject <subject> --content <content>\n'

        return msg

class ListMail():
    def __init__(self, package):
        self.package = package

    def parse(self):
        try:
            cursor, conn_id, _, db_cur, argv = utils.readPackage(self.package)
            if len(argv) > 0:
                msg = 'list-mail\n'
            elif not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                uname = cursor.get_uname(conn_id)
                db_cur.execute(f'''
                    select mail_subject, source_user, date_time 
                    from mail where target_user = "{uname}"
                    order by date_time
                ''')
                data = db_cur.fetchall()
                msg = f"{'ID':10}{'Subject':20}{'From':20}{'Date':20}\n"
                for idx, row in enumerate(data):
                    date = '/'.join(row[2].split(" ")[0].split('-')[1:])
                    msg += f'{idx+1:<10}{row[0]:20}{row[1]:20}{date:20}\n'
        except Exception as e:
            # print(e)
            msg = 'list-mail\n'

        return False, msg, []

class RetrMail():
    def __init__(self, package):
        self.package = package
    def parse(self):
        flag, addi_list = False, []
        try:
            cursor, conn_id, _, db_cur, argv = utils.readPackage(self.package)
            if not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            elif len(argv) != 1:
                msg = 'retr-mail <mail#>\n'
            else:
                uname, mail_id = cursor.get_uname(conn_id), int(argv[0])
                db_cur.execute(f'''
                    select mail_subject, source_user, date_time, upload_mail_name 
                    from mail where target_user = "{uname}"
                    order by date_time
                ''')
                data = db_cur.fetchall()

                if data is None or len(data) < mail_id or mail_id <= 0:
                    msg = 'No such mail.\n'
                else:
                    mail_subject, source_user, date_time, upload_mail_name = data[mail_id-1]
                    addi_list.extend([mail_subject, source_user, date_time, upload_mail_name])
                    msg = '\n'
                    flag = True
        except ValueError:
            msg = 'No such mail.\n'
        except Exception as e:
            # print(e)
            msg = 'retr-mail <mail#>\n'

        return flag, msg, addi_list

class DeleteMail():
    def __init__(self, package):
        self.package = package

    def parse(self):
        flag, addi_list = False, []
        try:
            cursor, conn_id, _, db_cur, argv = utils.readPackage(self.package)
            if len(argv) != 1:
                msg = 'delete-mail <mail#>\n'
            elif not cursor.check_login(conn_id):
                msg = 'Please login first.\n'
            else:
                uname, mail_id = cursor.get_uname(conn_id), int(argv[0])
                db_cur.execute(f'''
                    select mail_subject, date_time, upload_mail_name 
                    from mail where target_user = "{uname}"
                    order by date_time
                ''')
                data = db_cur.fetchall()

                if data is None or len(data) < mail_id or mail_id <= 0:
                    msg = 'No such mail.\n'
                else:
                    mail_subject, date_time, upload_mail_name = data[mail_id-1]

                    self.package['argv'].append(mail_subject)
                    self.package['argv'].append(date_time)
                    addi_list.append(upload_mail_name)
                    flag = True
                    msg = '\n'
        except ValueError:
            msg = 'No such mail.\n'
        except Exception as e:
            # print(e)
            msg = 'delete-mail <mail#>\n'

        return flag, msg, addi_list

    def process(self):
        try:
            cursor, conn_id, db_conn, db_cur, _ = utils.readPackage(self.package)
            
            uname = cursor.get_uname(conn_id)
            mail_subject, date_time = self.package['argv'][-2], self.package['argv'][-1]
            db_cur.execute(f'''
                delete from mail
                where target_user = "{uname}"
                and mail_subject = "{mail_subject}"
                and date_time = "{date_time}"
            ''')
            db_conn.commit()
            msg = 'Mail deleted.\n'
        except ValueError:
            msg = 'No such mail.\n'
        except Exception as e:
            # print(e)
            msg = 'delete-mail <mail#>\n'

        return msg