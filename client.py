import socket
import threading
import pickle
from server import GameComponents
# from messages import MessageCommand, MessageString


class Client:
  def __init__(self, game_manager):
       
    # This is used to get the local ip and address of this machine
    temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp.connect(("8.8.8.8", 80))
    self.localIP = temp.getsockname()[0] # DO NOT USE THE SECOND NUMBER
    temp.close()
    del temp

    self.game_manager = game_manager
    # self.client_loader = ClientLoader(game_manager)

    self.HEADER = 150
    self.PORT = 5051
    self.FORMAT = 'utf-8'
    self.DISCONNECT_MESSAGE = "!DISCONNECT"
    self.SERVER = "192.168.1.104"
    # self.SERVER = "192.168.1.122" #imac
    self.ADDR = (self.SERVER, self.PORT)

    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client.connect(self.ADDR)

    # This is the client waiting to recieve data from the server.
    serverInputThread = threading.Thread(target=self.handle_server_data, args=(), daemon=True)
    serverInputThread.start()

  def disconnect(self): # disconnecting from the host. This prob needs improvements.
    print('disconnecting from host')

    self.client.close()
    return


  # @measure_time
  def send(self, data): # Client sends this to the server
    self.client.send(data.encode(self.FORMAT))
    return


  
  def handle_server_data(self):
    recieved_data = self.client.recv(self.HEADER) # get own id
    self.client_loader.process_instructions(recieved_data)
    recieved_data = self.client.recv(4096) # large header for initial game loading
    self.client_loader.process_instructions(recieved_data)
    self.handle_active_server_data()
    return
    
  # @measure_time
  def handle_active_server_data(self):
    while True:
      recieved_data = self.client.recv(self.HEADER)
      

      # decoded_data = pickle.loads(recieved_data)
      # print('processing', recieved_data)
      """
      Process the data
      """
      # self.client_loader.process_instructions(recieved_data)
      disconnect = self.client_loader.process_instructions(recieved_data)
      if disconnect:
        self.disconnect()
        return
      
# send(DISCONNECT_MESSAGE) # need to implement a recurring ping message for people who dont properly exit