
# Import socket module 
import socket 
HOST = "127.0.0.1"
PORT = 6000 
  
def Main(): 
    client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
    message = "DATA\n"
    client.sendto(message, (HOST, PORT)) 
    data = client.recv(1024) 
    print('Received from the server :', str(data.decode('ascii'))) 
    client.close() 
  
if __name__ == '__main__': 
    Main() 

