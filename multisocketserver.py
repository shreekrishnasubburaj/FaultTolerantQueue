
# import socket programming library 
import socket 
  
# import thread module 
from _thread import *
import threading 
  
print_lock = threading.Lock() 

# thread Client function 
def thread6000(): 
    HOST = "127.0.0.1" 
    PORT = 6000
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    server.bind((HOST, PORT)) 
    print("Client port open at ", PORT) 
    while True: 
    	print("Listening for Client Requests") 
    	data, addr = server.recvfrom(1024) 
        if not data: 
  	    server.sendto("NACK\n", addr)
            print('Client Data invalid') 
  	else:
	    print(addr)
	    server.sendto("ACK\n", addr)
              
    #print_lock.release() 
    server.close() 
  
def thread5000(): 
    HOST = "127.0.0.1" 
    PORT = 5000
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    server.bind((HOST, PORT)) 
    print("Client port open at ", PORT) 
    while True: 
    	print("Listening for Client Requests") 
    	data, addr = server.recvfrom(1024) 
        if not data: 
  	    server.sendto("NACK\n", addr)
            print('Client Data invalid') 
  	else:
	    print(addr)
	    server.sendto("ACK\n", addr)
              
    #print_lock.release() 
    server.close() 
  
  
def Main(): 
    #print_lock.acquire() 
    t6000 = threading.Thread(target=thread6000, args=())
    t6000.start()
    t5000 = threading.Thread(target=threadClient, args=())
    t5000.start()
    #start_new_thread(threadClient, ()) 
    t6000.join() 
  
if __name__ == '__main__': 
    Main() 

