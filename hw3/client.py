from telnetlib import Telnet
import inspect
import boto3

class Client():
    def __init__(self, host, port):
        self.tn = Telnet(host, port)
        self.method_list = inspect.getmembers(self, predicate=inspect.ismethod)
        self.action_mapping = {
            'register': self.Register
        }
        self.s3_conn = boto3.resource('s3')

    def start(self):
        while True:
            try:
                read_msg = self.tn.read_until(b'% ').decode('utf-8')
                print(read_msg, end='')
                write_msg = input()
                self.tn.write(write_msg.encode('utf-8'))

                response = self.tn.read_until(b'\n').decode('utf-8').strip()
                response = response.split(' ')
                flag, msg = response[0], ' '.join(response[1:])

                flag = flag.split('$')
                flag, addi_list = flag[0], flag[1:]

                if flag == 'True':
                    write_msg = write_msg.split(' ')
                    cmd, argv = write_msg[0], write_msg[1:]
                    s3_flag = self.action_mapping[cmd](argv, addi_list)
                    self.tn.write(str(s3_flag).encode('utf-8'))
                elif flag == 'False':
                    print(msg)
                else:
                    print("ERROR")
                    raise EnvironmentError("Response ERROR!")

            except Exception as e:
                print(e)
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