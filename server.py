from socket import *
import time
from threading import Thread, Lock
from hashlib import md5
from pygame import mixer
from logger import Logger
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
    def __init__(self, md5_hash, client_length=5, total_length=8, ip = '0.0.0.0', port = 25565, debugging_mode = False):
        self.queue = []
        self.client_length = client_length
        self.total_length = total_length
        self.prefix_gen = get_prefix(self.total_length - self.client_length)
        self.md5_hash = md5_hash
        self.found = False
        self.passwd = None
        self.connections = {}
        self.addresses = []
        self.disconnected = []
        self.cur_work = {}
        self.last_seen = {}
        self.threads = {}
        self.ip = ip
        self.port = port
        self.logger = Logger(debugging_mode)
        self.lock = Lock()


    def mainloop(self):
        server_soc = socket()
        server_soc.setblocking(False)
        server_soc.bind((self.ip, self.port))
        server_soc.listen(2)
        self.logger.log_info('server started')
        while not self.found:
            try:
                cli_soc, addr = server_soc.accept()
                self.logger.log_info('client connected: {addr}'.format(addr=addr))
                self.connections[addr] = cli_soc
                self.addresses.append(addr)
                self.last_seen[addr] = time.time()
                self.cur_work[addr] = ""
                self.threads[addr] = Thread(target=self.handle_client, args=(cli_soc, addr))
                self.threads[addr].start()
            except:
                pass

        for soc in self.connections:
            try:
                soc.send("end".encode())
            except:
                pass

        t = Thread(target = self.playsound)
        t.start()
        time.sleep(0.001)

        for soc in self.connections.values():
            soc.close()
        
        self.logger.log_info('closed all connections')

        server_soc.close()
        self.logger.log_info('server closed')

        return self.passwd

    def playsound(self):
        mixer.init()
        mixer.music.load('ole.mp3')
        mixer.music.set_volume(1)
        mixer.music.play()
        time.sleep(47)

    def close_conn(self, addr):
        if not self.found:
            self.logger.log_warning("connection {addr} forcibly closed".format(addr=addr))
        self.disconnected.append(addr)
        self.connections[addr].close()
        del self.connections[addr]
        self.addresses.remove(addr)
        del self.last_seen[addr]
        del self.cur_work[addr]
        
    def get_disconnects(self):
        disconnects = self.disconnected
        self.disconnected = []
        return disconnects
        
    def handle_client(self, conn, addr):
        conn.settimeout(9999.0)
        conn.setblocking(True)
        print("Client {addr} connected".format(addr = addr))
        msg = conn.recv(4096).decode()

        while msg != "Hello":
            try:
                msg = conn.recv(4096).decode()
            except:
                self.close_conn(addr)
                return

        conn.send("ok".encode())
        self.last_seen[addr] = time.time()

        while True:
            try:
                msg = conn.recv(4096).decode()
                self.last_seen[addr] = time.time()
                if msg == "ready":
                    self.logger.log_debug("Client {addr} ready".format(addr=addr))

                    self.lock.acquire()
                    self.logger.log_debug("Client {addr} acquired mutex".format(addr=addr))

                    if self.queue == []:
                        self.queue.append(next(self.prefix_gen))
                    self.cur_work[addr] = self.queue.pop()
                    self.lock.release()
                    self.logger.log_debug("Client {addr} released mutex".format(addr=addr))

                    msg = '{0},{1},{2}'.format(self.md5_hash, self.cur_work[addr], self.client_length)
                    self.logger.log_debug('sent {addr} msg: {msg}'.format(addr=addr, msg=msg))
                    conn.send(msg.encode())

                elif msg[:5] == "found":
                    passwd = msg[6:]
                    if str(md5(passwd.encode()).hexdigest()) == self.md5_hash:
                        self.passwd = passwd
                        self.found = True
                        self.logger.log_info('{addr} found password: {password}'.format(addr = addr, password=self.passwd))
                        break
                    else:
                        self.logger.log_warning('{addr} sent wrong password'.format(addr=addr))
                        
            except:
                self.queue.append(self.cur_work[addr])
                self.close_conn(addr)
                
                break


def main():
    server = Server(str(md5("hello".encode()).hexdigest()), 3, 5)
    print(server.mainloop())


if __name__ == '__main__':
    main()