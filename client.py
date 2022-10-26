import select
from socket import *
import time


soc = socket()
soc.connect(("127.0.0.1", 25565))

soc.send("Hello".encode())
x = soc.recv(4096).decode()
print(x)

soc.send("ready".encode())
work = soc.recv(4096).decode()
print('smthing')
print(work)
soc.send("found,abc".encode())
print('found sent')
work = soc.recv(4096).decode()
print(work)