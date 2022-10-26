#import select
from socket import *
import time
from threading import Thread


"""
def crack_hashes():
    server_soc = socket()
    server_soc.setblocking(True)
    server_soc.bind((gethostname, 25565))
    server_soc.listen(2)
    readable = []
    work_mapping = dict()
    queue = [("aaaaaaa", "dddddddd")]
    hashed_pass = "900150983cd24fb0d6963f7d28e17f72"
    work_time = dict()
    passwd = None
    run = True

    while run:
        cli_soc, addr = server_soc.accept()

        rlist, wlist, elist = select.select([server_soc] + readable, [], [])

        for conn in rlist:
            if conn == server_soc:
                cli_soc, addr = server_soc.accept()
                readable.append(cli_soc)
            else:
                msg = conn.recv(4096).decode()
                if msg == "Hello":
                    conn.send("ok".encode())
                elif msg == "ready":
                    if queue == []:
                        pass
                    else:
                        work_mapping[conn] = queue[0]
                        conn.send(f'{hashed_pass},{queue[0][0]},{queue[0][1]}'.encode())
                        queue.pop(0)
                    work_time[conn] = time.time()
                elif msg[:5] == "found":
                    passwd = msg[6:]
                    run = False
                    for soc in readable:
                        soc.send("end".encode())
                    break
                else:
                    if time.time() - work_time[conn] > 100:
                        queue.append(work_mapping[conn])
                        del(work_time[conn])
                        del(work_mapping[conn])
                        conn.close()
    return passwd"""
class Server:
    def __init__(self, md5_hash):
        self.queue = []
        self.client_length = 5
        #self.prefix_gen
        self.md5_hash = md5_hash

    def handle_client(self, conn):
        conn.settimeout(30.0)
        msg = conn.recv(4096).decode()
        cur_work = ""

        while msg != "Hello":
            msg = conn.recv(4096).decode()

        conn.send("ok".encode())
        while True:
            try:
                msg = conn.recv(4096).decode()
                if msg == "ready":
                    if self.queue == []:
                        pass
                    else:
                        cur_work = self.queue.pop()
                        conn.send(f'{self.md5_hash},{cur_work},{self.client_length}'.encode())

                elif msg[:5] == "found":
                    passwd = msg[6:]
                    #change flag
            except:
                conn.close()
                self.queue.append(cur_work)
                break
    def get_prefix(length):
        prefix = "a"*length
        while prefix != "z"*length:
            yield prefix
            if prefix[-1] == "z":
                prefix = prefix[:-1] + "a"
                for i in range(length-2, -1, -1):
                    if prefix[i] == "z":
                        prefix = prefix[:i] + "a" +  + prefix[i+1:]
                    else:
                        prefix = prefix[:i] + chr(ord(prefix[i]) + 1) + prefix[i+1:]
                        break
            else:
                prefix = prefix[:-1]+chr(ord(prefix[-1]) + 1)

def main():
    password = crack_hashes()
    print(password)


if __name__ == '__main__':
    main()
