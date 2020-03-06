
# import socket programming library 
import socket 
import pickle
# import thread module 
from _thread import *
import threading 
import sys
import random
import time
import heapq
PORT = int(sys.argv[1])
HOST = "127.0.0.1"
#print(PORT, type(PORT))
idCounter = 0 
FTQueue = {}  
labelIdMap = {}
buffer1 = []
buffer2 = []
buffer3 = []
GS = 0
pid = PORT
n = 3

def performOperation(msg):
    global idCounter
    opt = msg.OP[0]
    if opt == 0: #qCreate
        label = msg.OP[1]
        if label in labelIdMap:
            print(FTQueue[labelIdMap[label]])
            return labelIdMap[label]
        else:
            labelIdMap[label] = idCounter
            FTQueue[idCounter] = []
            print(FTQueue[labelIdMap[label]])
            idCounter+=1
            return idCounter-1
    
    elif opt == 1: #qDestroy
        id = msg.OP[1]
        if id in FTQueue:
            del FTQueue[id]
            for key, val in labelIdMap.items():
                if val==id:
                    break
            del labelIdMap[key]

    elif opt == 2: #qId
        label = msg.OP[1]
        if label in labelIdMap:
            print(FTQueue[labelIdMap[label]])
            return labelIdMap[label]
        else:
            return -1

    elif opt == 3: #qPush
        id = msg.OP[1]
        item = msg.OP[2]
        if id in FTQueue:
            FTQueue[id].append(item)
            print(FTQueue[id])

    elif opt == 4: #qPop
        id = msg.OP[1]
        if id in FTQueue:
            if FTQueue[id]:
                item = FTQueue[id].pop(0)
                print(FTQueue[id])
                return item
    
    elif opt == 5: #qTop
        id = msg.OP[1]
        if id in FTQueue:
            if FTQueue[id]:
                print(FTQueue[id])
                return FTQueue[id][0]

    elif opt == 6: #qSize
        id = msg.OP[1]
        if id in FTQueue:
            print(FTQueue[id])
            return len(FTQueue[id])



class Message(object):
    def __init__(self, GS: int, GSReq: int, mId: int, OP: int, clAddr: str, sendAddr: str):
        self.GS = GS
        self.GSReq = GSReq
        self.mId = mId
        self.OP = OP
        self.clAddr = clAddr
        self.sendAddr = sendAddr

    def __repr__(self):
        return f'Message- \n\tGS:{self.GS}, \n\tmId:{self.mId}, \n\tOP:{self.OP}, \n\tclAddr:{self.clAddr}, \n\tsendAddr:{self.sendAddr}'

    def __lt__(self, other):
        return self.GS < other.GS 

dummy = Message(-1, -1, 1234, [0, 1, 2], "127.0.0.1:6000", "127.0.0.1:5000")
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

def sendOperation(addr="127.0.0.1", port=5000, msg=dummy):
    sock.sendto(pickle.dumps(msg), (addr, port))

def broadcast(msg=dummy):
    for i in range(1,n+1):
        port = 5000+i
        addr = "127.0.0.1"
        sendOperation(addr, port, msg)

# thread Client function 
def thread6000(): 
    CHOST = "127.0.0.1" 
    CPORT = int(sys.argv[2]) 
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.bind((CHOST, CPORT)) 
    print("Server port open at", CPORT) 
    while True: 
        print("Listening for Client Requests\n") 
        data, addr = server.recvfrom(1024) 
        print("Request Recieved from ", addr)
        print("Broadcasting to all servers...")
        mid = random.randint(1,100001)
        if not data:
            server.sendto("NACK\n", addr)
            print('Client Data invalid\n')
        else:
            msg = pickle.loads(data)
            msg.GS = -1
            msg.Req = -1
            msg.mId = mid
            msg.clAddr = str(str(addr[0])+":"+str(addr[1]))
            msg.sendAddr = str(str(HOST)+":"+str(PORT))
            broadcast(msg)
            #server.sendto(pickle.dumps("ACK\n"), addr)
              
    #print_lock.release() 
    server.close() 


def thread5000(): 
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.bind((HOST, PORT)) 
    print("Server port open at", PORT) 
    while True:
        print("Listening for Peer Server Requests\n") 
        data, addr = server.recvfrom(1024) 
        if not data:
            server.sendto("NACK\n", addr)
            print('Server Data invalid\n')
        else:
            #print(pickle.loads(data))
            #print(addr)
            heapq.heappush(buffer1, pickle.loads(data))
	    #server.sendto("ACK\n", addr)
              
    #print_lock.release() 
    server.close() 
  
def Main(): 
    global GS
    global n
    global pid
    #print_lock.acquire() 
    t6000 = threading.Thread(target=thread6000, args=())
    t6000.start()
    t5000 = threading.Thread(target=thread5000, args=())
    t5000.start()
    while True:
        if buffer1:
            nextMsg = heapq.nlargest(1, buffer1)[0]
            buffer1.remove(nextMsg)
            print(nextMsg) 
            if nextMsg.GS==-2: #NACK
                for msg in buffer2:
                    if msg.GS==nextMsg.GSReq:
                        addr = nextMsg.sendAddr.split(":")[0]
                        port = int(nextMsg.sendAddr.split(":")[1])
                        sendOperation(addr, port ,msg) #send msg to requesting server
            elif nextMsg.GS==-1: #Sequencer needs to set GS
                if (nextMsg.mId%n)+1==(pid%10):
                    newMsg = Message(GS+1, -1, nextMsg.mId, nextMsg.OP, nextMsg.clAddr, str(HOST)+":"+str(PORT))
                    buffer2.append(newMsg)
                    broadcast(newMsg)        
            else: #normal message
                if nextMsg.GS<=GS: #duplicate
                    continue
                elif nextMsg.GS==GS+1: #in-order
                    result = -2
                    result = performOperation(nextMsg)
                    GS+=1
                    if (nextMsg.mId%n)+1==pid%10:
		        #Send result to client
                        addr = nextMsg.clAddr.split(":")[0]
                        port = int(nextMsg.clAddr.split(":")[1])
                        sock.sendto(pickle.dumps(result), (addr, port))
                    while buffer3 and buffer3[0].GS==GS+1:
                        nextMsg = heapq.heappop(buffer3)
                        performOperation(nextMsg)
                        GS+=1
                else: #out-of-order
                    heapq.heappush(buffer3, nextMsg)
                    #create NAC and send to seq
                    Nackmsg = Message(-2, GS+1, 1234, [-1, -2, -3], "127.0.0.1", str(HOST)+":"+str(PORT))
                    broadcast(Nackmsg)


if __name__ == '__main__': 
    Main() 

