from socket import *
import time
from threading import Thread
from hashlib import md5
from pygame import mixer
# 10.30.56.225
# 25565
def get_prefix(length):
    prefix = "a" * length
    while prefix != "z" * length:
        yield prefix
        if prefix[-1] == "z":
            prefix = prefix[:-1] + "a"
            for i in range(length - 2, -1, -1):
                if prefix[i] == "z":
                    prefix = prefix[:i] + "a" + prefix[i + 1:]
                else:
                    prefix = prefix[:i] + chr(ord(prefix[i]) + 1) + prefix[i + 1:]
                    break
        else:
            prefix = prefix[:-1] + chr(ord(prefix[-1]) + 1)
    yield prefix


class Server:
    def __init__(self, md5_hash, client_length=5, total_length=8):
        self.queue = []
        self.client_length = client_length
        self.total_length = total_length
        self.prefix_gen = get_prefix(self.total_length - self.client_length)
        self.md5_hash = md5_hash
        self.found = False
        self.passwd = None

    def mainloop(self):
        server_soc = socket()
        server_soc.setblocking(False)
        server_soc.bind(('0.0.0.0', 25565))
        server_soc.listen(2)
        connections = []
        print("Server started")
        while not self.found:
            try:
                cli_soc, addr = server_soc.accept()
                connections.append(cli_soc)
                Thread(target=self.handle_client, args=(cli_soc, addr)).start()
            except:
                pass

        for soc in connections:
            try:
                soc.send("end".encode())
            except:
                pass

        t = Thread(target = self.playsound)
        t.start()
        time.sleep(0.001)
        for soc in connections:
            soc.close()

        server_soc.close()
        return self.passwd

    def playsound(self):
        mixer.init()
        mixer.music.load('ole.mp3')
        mixer.music.set_volume(1)
        mixer.music.play()
        time.sleep(47)

    def handle_client(self, conn, addr):
        conn.settimeout(9999.0)
        conn.setblocking(True)
        print("Client {addr} connected".format(addr = addr))
        msg = conn.recv(4096).decode()
        cur_work = ""

        while msg != "Hello":
            try:
                msg = conn.recv(4096).decode()
            except:
                print("connection {addr} closed".format(addr=addr))
                conn.close()
                return


        conn.send("ok".encode())
        while True:
            try:
                msg = conn.recv(4096).decode()
                if msg == "ready":
                    print("Client {addr} ready".format(addr=addr))
                    while self.queue == []:
                        try:
                            self.queue.append(next(self.prefix_gen))
                        except:
                            time.sleep(0.001)

                    cur_work = self.queue.pop()
                    msg = '{0},{1},{2}'.format(self.md5_hash, cur_work, self.client_length)
                    print('sent {addr} msg: {msg}'.format(addr=addr, msg=msg))
                    conn.send(msg.encode())

                elif msg[:5] == "found":
                    passwd = msg[6:]
                    if str(md5(passwd.encode()).hexdigest()) == self.md5_hash:
                        self.passwd = passwd
                        self.found = True
                        break

            except:
                print("connection {addr} closed".format(addr=addr))
                conn.close()
                self.queue.append(cur_work)
                break


def main():
    server = Server(str(md5("catwalk".encode()).hexdigest()), 5, 7)
    print(server.mainloop())


if __name__ == '__main__':
    main()