import socket
from hashlib import md5
from threading import Thread
from multiprocessing import Process
FOUND = False
ANSWER = ''
data = None
s = None

def ServerConnect():
    global FOUND, data, s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 25565)
    s.connect(server_address)
    print("Connected")
    s.send("Hello".encode())
    ok = s.recv(1024).decode()
    assert ok == 'ok'
    s.send("ready".encode())
    data = s.recv(1024).decode()
    threadEnd = Thread(target = listenForEnd , args = (s,))
    threadEnd.start()
    while not FOUND:
        print("ready")
        hash,prefix,num = data.split(',')
        num = int(num)
        threads = []
        for i in range(26):
            thread = Thread(target = engine , args = (hash,prefix + chr(97+i),num -1))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        if FOUND:
            print("found",ANSWER)
        else:
            print("Cant Found!")
            old_data = data
            s.sendall(b"ready")
            print("weeeee")
            while old_data == data:
                pass
        print(FOUND)
            

def listenForEnd(s):
    global data, FOUND
    while not FOUND:
        temp = s.recv(1024).decode()
        if temp == "end":
            FOUND = True
        else:
            data = temp

def HashChecking(hash,prefix,str):
    str = prefix + "".join(str)
    return md5(str.encode()).hexdigest() == hash

def engine(hash,prefix,num):
    global FOUND, ANSWER, s
    start = ['a']*num
    while not FOUND:
        if HashChecking(hash, prefix,start):
            FOUND = True
            ANSWER = prefix + "".join(start)
            s.sendall(f"found,{ANSWER}".encode())
        start = StrUp(start)
        if start == ['a'] * num: return FOUND
    
    
def StrUp(str):
    for i in range(len(str)):
        if str[-1-i] =='z':
            str[-1-i] = 'a'
        else:
            str[-1-i] = chr(ord(str[-1-i])+1)
            break
    return str


def main():
    ServerConnect()
    
if __name__ == '__main__':
    main()