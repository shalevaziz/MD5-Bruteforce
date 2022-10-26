#import select
import imp
from socket import *
import time
from threading import Thread
from hashlib import md5


def get_prefix(length):
    prefix = "a" * length
    while prefix != "z"*length:
        yield prefix
        if prefix[-1] == "z":
            prefix = prefix[:-1] + "a"
            for i in range(length-2, -1, -1):
                if prefix[i] == "z":
                    prefix = prefix[:i] + "a" + + prefix[i+1:]
                else:
                    prefix = prefix[:i] + \
                        chr(ord(prefix[i]) + 1) + prefix[i+1:]
                    break
        else:
            prefix = prefix[:-1]+chr(ord(prefix[-1]) + 1)


class Server:
    def __init__(self, md5_hash, client_length=5, total_length=8):
        self.queue = []
        self.client_length = client_length
        self.total_length = total_length
        self.prefix_gen = get_prefix(self.total_length-self.client_length)
        self.md5_hash = md5_hash
        self.found = False
        self.passwd = None

    def mainloop(self):
        server_soc = socket()
        server_soc.setblocking(False)
        server_soc.bind(('127.0.0.1', 25565))
        server_soc.listen(2)
        connections = []
        Threads = []
        print("Server started")
        while not self.found:
            try:
                cli_soc, addr = server_soc.accept()
                connections.append(cli_soc)
                Thread(target=self.handle_client, args=(cli_soc,)).start()
            except:
                pass

        for soc in connections:
            soc.send("end".encode())

        time.sleep(0.001)
        for soc in connections:
            soc.close()

        server_soc.close()
        return self.passwd

    def handle_client(self, conn):
        conn.settimeout(30.0)
        conn.setblocking(True)
        print("Client connected")
        msg = conn.recv(4096).decode()
        cur_work = ""

        while msg != "Hello":
            msg = conn.recv(4096).decode()

        conn.send("ok".encode())
        while True:
            try:
                msg = conn.recv(4096).decode()
                if msg == "ready":
                    print("Client ready")
                    if self.queue == []:
                        self.queue.append(next(self.prefix_gen))

                    cur_work = self.queue.pop()
                    conn.send(
                        f'{self.md5_hash},{cur_work},{self.client_length}'.encode())

                elif msg[:5] == "found":
                    passwd = msg[6:]
                    if str(md5(passwd.encode()).hexdigest()) == self.md5_hash:
                        self.passwd = passwd
                        self.found = True
                        break
            except:
                conn.close()
                self.queue.append(cur_work)
                break


def main():
    server = Server("900150983cd24fb0d6963f7d28e17f72")
    print(server.mainloop())


if __name__ == '__main__':
    main()
