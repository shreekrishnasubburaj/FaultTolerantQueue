import heapq
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

buffer1 = []
buffer2 = []
buffer3 = []
Addr = ""
pid = 1
GS = 0

while True:
    if buffer1:
        nextMsg = buffer1.pop()
        if nxtMsg.GS==-2: #NACK
            for msg in buffer2:
                if msg.GS==nextMsg.GSReq:
                    #send msg to requesting server
                    print("a")
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