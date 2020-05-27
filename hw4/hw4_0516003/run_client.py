import client
import sys
import redis

def handler(message):
    if type(message['data']) != int:
        print(message['data'].decode('utf-8'))
        print('% ', end='', flush=True)

if __name__ == "__main__":
    try:
        host, port = sys.argv[1], int(sys.argv[2])
        port = int(port)
    except:
        print("Usage: python3 host_addr host_port")

    red = redis.Redis(host='localhost', port=6379, db=0)
    pub = red.pubsub()
    pub.psubscribe(**{'': lambda x: x})
    pub.punsubscribe()
    thread = pub.run_in_thread(sleep_time=0.001)

    process = client.Client(host, port, red, pub)
    process.start()

    thread.stop()