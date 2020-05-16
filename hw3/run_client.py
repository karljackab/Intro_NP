import client
import sys

if __name__ == "__main__":
    try:
        host, port = sys.argv[1], int(sys.argv[2])
        port = int(port)
    except:
        print("Usage: python3 host_addr host_port")
    
    process = client.Client(host, port)
    process.start()