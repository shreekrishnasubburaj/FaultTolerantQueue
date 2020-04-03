class Message(object):
    def __init__(self, GS: int, GSReq: int, mId: int, OP: list, clAddr: str, sendAddr: str):
        self.GS = GS
        self.GSReq = GSReq
        self.mId = mId 
        self.OP = OP
        self.clAddr = clAddr
        self.sendAddr = sendAddr

    def __repr__(self):
        return f'Message- GS:{self.GS}, mId:{self.mId}, OP:{self.OP}, clAddr:{self.clAddr}, sendAddr        :{self.sendAddr}'

    def __lt__(self, other):
        return self.GS < other.GS

dummycreate = Message(-1, -1, 123, [0, 1], "127.0.0.1", "127.0.0.1")
dummygetid = Message(-1, -1, 2211, [2, 1], "127.0.0.1", "127.0.0.1")
dummypush1 = Message(-1, -1, 544, [3, 0, 1], "127.0.0.1", "127.0.0.1")
dummypush2 = Message(-1, -1, 3431, [3, 0, 2], "127.0.0.1", "127.0.0.1")
dummypush3 = Message(-1, -1, 32, [3, 0, 3], "127.0.0.1", "127.0.0.1")
dummysize = Message(-1, -1, 2330, [6, 0], "127.0.0.1", "127.0.0.1")
dummypop = Message(-1, -1, 71, [4, 0], "127.0.0.1", "127.0.0.1")
dummytop = Message(-1, -1, 6761, [5, 0], "127.0.0.1", "127.0.0.1")
dummydestroy = Message(-1, -1, 891, [1, 0], "127.0.0.1", "127.0.0.1")
msgList = [dummycreate, dummygetid, dummypush1, dummypush2,
dummypush3, dummysize, dummypop, dummytop]

# Import socket module 
import socket 
import pickle
import sys
import time
HOST = "127.0.0.1"
PORT = int(sys.argv[1]) 
  
def Main(): 
    global PORT
    client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
    time.sleep(2)
    # client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # client.sendto(pickle.dumps(dummycreate), (HOST, 6001))
    # data = client.recv(1024) 
    # print('Received from the server :', pickle.loads(data)) 
    # time.sleep(10)
    # client.sendto(pickle.dumps(dummypush1), (HOST, 6003))
    # data = client.recv(1024) 
    # print('Received from the server :', pickle.loads(data)) 
    for l in msgList:
       message = l
       PORT += 1
       client.sendto(pickle.dumps(message), (HOST, 6001)) 
       data = client.recv(1024) 
       print('Received from the server :', pickle.loads(data)) 
       #time.sleep(2)
    client.close() 
  
if __name__ == '__main__': 
    Main() 

