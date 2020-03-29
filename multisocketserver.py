
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
if len(sys.argv) < 2:
    print("Usage: python multisocketserver.py SERVER_NUMBER")
    sys.exit()

class procSetVal(object):
    def __init__(self, CID, VID):
        self.CID = CID
        self.VID = VID
    
    def __ne__(self, other):
        return (self.CID!=other.CID or self.VID!=other.VID)

    def __eq__(self, other):
        return (self.CID==other.CID and self.VID==other.VID)
    
    def __repr__(self):
        return f'CID: {self.CID} VID: {self.VID}'

    def __hash__(self):
        return hash(str(self.CID)+","+str(self.VID))


TRAN=0
procSetOld = set()
procSetOld.add(procSetVal(-1, 1))
procSetOld.add(procSetVal(-1, 2))
#procSetOld.add(procSetVal(-1, 3))
procSetNew = set()

CID = -1
VID = int(sys.argv[1])
PORT = 5000+VID
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
            #print(FTQueue[labelIdMap[label]])
            return labelIdMap[label]
        else:
            labelIdMap[label] = idCounter
            FTQueue[idCounter] = []
            #print(FTQueue[labelIdMap[label]])
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
            #print(FTQueue[labelIdMap[label]])
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
                #print(FTQueue[id])
                return FTQueue[id][0]

    elif opt == 6: #qSize
        id = msg.OP[1]
        if id in FTQueue:
            #print(FTQueue[id])
            return len(FTQueue[id])


class Message(object):
    def __init__(self, GS, GSReq, mId, OP, clAddr, sendAddr, FTQ={}):
        self.GS = GS
        self.GSReq = GSReq
        self.mId = mId
        self.OP = OP
        self.clAddr = clAddr
        self.sendAddr = sendAddr
        self.FTQ = FTQ

    def __repr__(self):
        return f'Message- \n\tGS:{self.GS}, \n\tmId:{self.mId}, \n\tOP:{self.OP}, \n\tclAddr:{self.clAddr}, \n\tsendAddr:{self.sendAddr}'

    def __lt__(self, other):
        return (self.GS < other.GS and self.GS > 0 and other.GS > 0)

dummy = Message(-1, -1, 1234, [0, 1, 2], "127.0.0.1:6000", "127.0.0.1:5000")
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

def sendOperation(addr="127.0.0.1", port=5000, msg=dummy):
    sock.sendto(pickle.dumps(msg), (addr, port))

def broadcast(msg=dummy, level=5000):
    for i in range(1,n+1):
        port = level+i
        addr = "127.0.0.1"
        sendOperation(addr, port, msg)

def thread7000(): #transition logic
    aliveSenderPORT = 8000+int(sys.argv[1])
    global TRAN
    while True:
        if TRAN==0:
            time.sleep(5)
            print(procSetOld, end='')
            print(procSetNew)
            if procSetOld!=procSetNew:
                transitionMessage = Message(-2, -1, -1, -1, [], str(HOST)+":"+str(aliveSenderPORT))
                broadcast(transitionMessage, level=9000)
            else:
                time.sleep(2)
                procSetNew.clear()
        else:
            time.sleep(2)
            print("TRANSITION:", int(sys.argv[1]))
            #remaining transition logic

def thread8000(): #send alive messages
    global CID
    global VID
    HOST = "127.0.0.1"
    aliveSenderPORT = 8000+int(sys.argv[1]) 
    while True:
        aliveMessage = Message(CID, VID, -1, -1, [], str(HOST)+":"+str(aliveSenderPORT))
        broadcast(aliveMessage, level=9000)
        time.sleep(.2) #send alive every 200 milliseconds

def thread9000(): #receive alive/transition message
    global CID
    global VID
    global TRAN
    aliveReceiverPORT = 9000+int(sys.argv[1]) 
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    # server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.bind((HOST, aliveReceiverPORT)) 
    print("Listening for Alive Messages\n") 
    while True:
        procSetNew.add(procSetVal(CID, VID))
        data, addr = server.recvfrom(1024) 
        msg = pickle.loads(data)
        if msg.GS!=-2: #alive message
            sender = msg.sendAddr
            procSetNew.add(procSetVal(msg.GS, msg.GSReq))
            # procSetNew.add(int(sender.split(":")[1])%10)
            #print(procSetNew)
        else:   #transition message
            print("Transition message received")
            TRAN = 1
    server.close() 


# thread Client function 
def thread6000(): 
    CHOST = "127.0.0.1" 
    CPORT = 6000+int(sys.argv[1]) 
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    # server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
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
            msg.mId = msg.mId
            msg.clAddr = str(str(addr[0])+":"+str(addr[1]))
            msg.sendAddr = str(str(HOST)+":"+str(PORT))
            broadcast(msg)
            #server.sendto(pickle.dumps("ACK\n"), addr)
              
    #print_lock.release() 
    server.close() 


def thread5000(): 
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    # server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
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
    global TRAN
    #print_lock.acquire() 
    t6000 = threading.Thread(target=thread6000, args=())
    t6000.start()
    t5000 = threading.Thread(target=thread5000, args=())
    t5000.start()
    t7000 = threading.Thread(target=thread7000, args=())
    t7000.start()
    t8000 = threading.Thread(target=thread8000, args=())
    t8000.start()
    t9000 = threading.Thread(target=thread9000, args=())
    t9000.start()
    totalorder = []
    while True:
        if buffer1:
            if TRAN==0:
                nextMsg = heapq.heappop(buffer1)
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
                        totalorder.append([GS+1, nextMsg.OP])
                        result = -2
                        result = performOperation(nextMsg)
                        GS+=1
                        for l in totalorder:
                            print(l)
                        if (nextMsg.mId%n)+1==pid%10:
                            #Send result to client
                            addr = nextMsg.clAddr.split(":")[0]
                            port = int(nextMsg.clAddr.split(":")[1])
                            sock.sendto(pickle.dumps(result), (addr, port))
                        while buffer3 and buffer3[0].GS==GS+1:
                            nextMsg = heapq.heappop(buffer3)
                            print("**********")
                            print(nextMsg)
                            print("**********")
                            totalorder.append([GS+1, nextMsg.OP])
                            performOperation(nextMsg)
                            GS+=1
                            for l in totalorder:
                                print(l)
                    else: #out-of-order
                        heapq.heappush(buffer3, nextMsg)
                        #create NAC and send to seq
                        Nackmsg = Message(-2, GS+1, 1234, [-1, -2, -3], "127.0.0.1", str(HOST)+":"+str(PORT))
                        broadcast(Nackmsg)
            else:
                print("Messaging Suspended")
                time.sleep(2)

if __name__ == '__main__': 
    Main() 

