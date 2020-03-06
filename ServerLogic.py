import heapq
import socket

class Message(object):
    def __init__(self, GS: int, GSReq: int, mId: int, OP: int, clAddr: str, sendAddr: str):
        self.GS = GS
        self.GSReq = GSReq
        self.mId = mId
        self.OP = OP
        self.clAddr = clAddr
        self.sendAddr = sendAddr

    def __repr__(self):
        return f'Message- GS:{self.GS}, mId:{self.mId}, OP:{self.OP}, clAddr:{self.clAddr}, sendAddr:{self.sendAddr}'

    def __lt__(self, other):
        return self.GS < other.GS

idCounter = 0
FTQueue = {}  
labelIdMap = {}
buffer1 = []
buffer2 = []
buffer3 = []
HOST = ""
PORT = 2
pid = PORT
GS = 0


    
def performOperation(msg):
    opt = msg.OP[0]
    if opt == 0: #qCreate
        label = msg.OP[1]
        if label in labelIdMap:
            return labelIdMap[label]
        else:
            labelIdMap[label] = idCounter
            FTQueue[idCounter] = []
            idCounter+=1
            return idCounter-1
        
    elif opt == 1: #qDestroy
        id = msg.OP[1]
        if id in FTQueue:
            del FTQueue[id]
        
    elif opt == 2: #qId
        label = msg.OP[1]
        if label in labelIdMap:
            return labelIdMap[label]
        else:
            return -1
        
    elif opt == 3: #qPush
        id = msg.OP[1]
        item = msg.OP[2]
        if id in FTQueue:
            FTQueue[id].append(item)
        
    elif opt == 4: #qPop
        id = msg.OP[1]
        if id in FTQueue:
            if FTQueue[id]:
                item = FTQueue[id].pop(0)
                return item
    elif opt == 5: #qTop
        id = msg.OP[1]
        if id in FTQueue:
            if FTQueue[id]:
                return FTQueue[id][0]
        
    elif opt == 6: #qSize
        id = msg.OP[1]
        if id in FTQueue:
            return len(FTQueue[id])

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
while True:
    if buffer1:
        nextMsg = buffer1.pop()
        if nxtMsg.GS==-2: #NACK
            for msg in buffer2:
                if msg.GS==nextMsg.GSReq:
                    server.sendto(msg, sendAddr) #send msg to requesting server
        elif nxtMsg.GS==-1: #Sequencer needs to set GS
            if nextMsg.mid%n==pid:
                newMsg = Message(GS+1, nextMsg.mId, nextMsg.OP, nextMsg.clAddr, Addr)
                buffer2.append(newMsg)
                #broadcast newMsg        
        else: #normal message
            if nextMsg.GS<=GS: #duplicate
                continue
            elif nextMsg.GS==GS+1: #in-order
                result = performOperation(nextMsg)
                GS+=1
                if nextMsg.mid%n==pid:
                    #return result to client
                    print("b")
                while buffer3 and buffer3[0].GS==GS+1:
                    nextMsg = buffer3.heappop()
                    performOperation(nextMsg)
                    GS+=1
            else: #out-of-order
                heapq.heappush(buffer3, nxtMsg)
                #create NAC and send to seq