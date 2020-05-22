from telnetlib import Telnet
import inspect
import boto3
import os

class Client():
    def __init__(self, host, port):
        self.telnet = Telnet(host, port)
        self.method_list = inspect.getmembers(self, predicate=inspect.ismethod)
        self.action_mapping = {
            'register': self.Register,
            'login': self.Login,
            'logout': self.Logout,
            'create-post': self.CreatePost,
            'comment': self.Comment,
            'read': self.Read,
            'delete-post': self.DeletePost,
            'update-post': self.UpdatePost,
            'mail-to': self.MailTo,
            'retr-mail': self.RetrMail,
            'delete-mail': self.DeleteMail
        }
        self.s3_conn = boto3.resource('s3')
        self.bucket = None

    def start(self):
        while True:
            try:
                read_msg = self.telnet.read_until(b'% ').decode('utf-8')
                print(read_msg, end='')
                write_msg = input()
                # print(f'write {write_msg}')
                if write_msg == '':
                    write_msg = ' \n'
                self.telnet.write(write_msg.encode('utf-8'))
                response = self.telnet.read_until(b'\n').decode('utf-8').strip()
                # print(response)
                response = response.split('|')
                # print(response)
                flag, msg = response[0], ' '.join(response[1:])
                # print(flag, msg)
                flag = flag.split('$')
                flag, addi_list = flag[0], flag[1:]

                write_msg = write_msg.split(' ')
                cmd, argv = write_msg[0], write_msg[1:]
                if flag == 'True':
                    s3_flag = self.action_mapping[cmd](argv, addi_list)
                    self.telnet.write(str(s3_flag).encode('utf-8'))
                elif flag == 'False':
                    if cmd == 'exit':
                        break
                    print(msg)
                else:
                    raise EnvironmentError("Response ERROR!")

            except Exception as e:
                # print(e)
                break

    def Register(self, argv, addi_list):
        flag = False
        try:
            bucket_name = addi_list[0]
            self.s3_conn.create_bucket(Bucket=bucket_name)
            flag = True
        except Exception as e:
            print(e)
            pass
        return flag
    
    def Login(self, argv, addi_list):
        flag = False
        try:
            bucket_name = addi_list[0]
            self.bucket = self.s3_conn.Bucket(bucket_name)
            flag = True
        except Exception as e:
            print(e)

        return flag
    
    def Logout(self, argv, addi_list):
        flag = False
        try:
            self.bucket = None
            flag = True
        except Exception as e:
            print(e)

        return flag
    
    def CreatePost(self, argv, addi_list):
        flag = False
        try:
            upload_file_name = addi_list[0]
            t_idx = argv.index('--title')
            c_idx = argv.index('--content')

            if t_idx < c_idx:
                content = ' '.join(argv[c_idx+1:]).replace('<br>','\n')
            else:
                content = ' '.join(argv[c_idx+1:t_idx]).replace('<br>','\n')

            with open(f'/tmp/{upload_file_name}', 'w') as f:
                f.write(content)

            self.bucket.upload_file(f'/tmp/{upload_file_name}', upload_file_name)
            flag = True
            os.remove(f'/tmp/{upload_file_name}')
        except Exception as e:
            print(e)

        return flag
    
    def Comment(self, argv, addi_list):
        flag = False
        try:
            bucket_name, upload_comment_name = addi_list
            target_bucket = self.s3_conn.Bucket(bucket_name)
            content = ' '.join(argv[1:])
            with open(f'/tmp/{upload_comment_name}', 'w') as f:
                f.write(content)
            target_bucket.upload_file(f'/tmp/{upload_comment_name}', upload_comment_name)
            flag = True
            os.remove(f'/tmp/{upload_comment_name}')
        except Exception as e:
            print(e)

        return flag
    
    def Read(self, argv, addi_list):
        try:
            author, title, date_time, upload_file_name, bucket_name = \
                addi_list[0], addi_list[1], addi_list[2], addi_list[3], addi_list[4]

            target_bucket = self.s3_conn.Bucket(bucket_name)
            target_object = target_bucket.Object(upload_file_name)
            content = target_object.get()['Body'].read().decode()

            msg = f"Author\t:{author}\nTitle\t:{title}\nDate\t:{date_time.split(' ')[0]}\n--\n{content}\n--\n"

            for idx in range(5, len(addi_list), 2):
                commenter, upload_comment_name = addi_list[idx], addi_list[idx+1]
                target_object = target_bucket.Object(upload_comment_name)
                content = target_object.get()['Body'].read().decode()

                msg += f"{commenter}: {content}\n"
            print(msg, end='')
        except Exception as e:
            print(e)

        return False

    def DeletePost(self, argv, addi_list):
        flag = False
        try:
            bucket_name = addi_list[0]
            target_bucket = self.s3_conn.Bucket(bucket_name)
            for hash_code in addi_list[1:]:
                target_object = target_bucket.Object(hash_code)
                target_object.delete()
            flag = True
        except Exception as e:
            print(e)

        return flag

    def UpdatePost(self, argv, addi_list):
        try:
            bucket_name, upload_file_name, new_content = addi_list
            new_content = new_content.replace('<br>','\n')
            target_bucket = self.s3_conn.Bucket(bucket_name)

            with open(f'/tmp/{upload_file_name}', 'w') as f:
                f.write(new_content)
            target_bucket.upload_file(f'/tmp/{upload_file_name}', upload_file_name)
            os.remove(f'/tmp/{upload_file_name}')
            print('Update successfully.')
        except Exception as e:
            print(e)

        return False
    
    def MailTo(self, argv, addi_list):
        flag = False
        try:
            target_bucket_name, mail_name = addi_list
            target_bucket = self.s3_conn.Bucket(target_bucket_name)

            s_idx = argv.index('--subject')
            c_idx = argv.index('--content')

            if s_idx < c_idx:
                content = ' '.join(argv[c_idx+1:]).replace('<br>','\n')
            else:
                content = ' '.join(argv[c_idx+1:s_idx]).replace('<br>','\n')

            with open(f'/tmp/{mail_name}', 'w') as f:
                f.write(content)

            target_bucket.upload_file(f'/tmp/{mail_name}', mail_name)
            flag = True
            os.remove(f'/tmp/{mail_name}')
        except Exception as e:
            print(e)

        return flag
    
    def RetrMail(self, argv, addi_list):
        try:
            mail_subject, source_user, date_time, upload_mail_name = addi_list

            mail_object = self.bucket.Object(upload_mail_name)
            content = mail_object.get()['Body'].read().decode()

            msg = f"Subject\t:{mail_subject}\nFrom\t:{source_user}\nDate\t:{date_time.split(' ')[0]}\n--\n{content}\n--\n"
            print(msg, end='')
        except Exception as e:
            print(e)

        return False
    
    def DeleteMail(self, argv, addi_list):
        flag = False
        try:
            upload_mail_name = addi_list[0]
            target_mail = self.bucket.Object(upload_mail_name)
            target_mail.delete()
            flag = True
        except Exception as e:
            print(e)

        return flag