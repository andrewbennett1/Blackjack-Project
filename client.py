import socket
import threading
import pickle
import rules

class Client:
  def __init__(self, game_scene):
    # This is used to get the local ip and address of this machine
    temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp.connect(("8.8.8.8", 80))
    self.localIP = temp.getsockname()[0] # DO NOT USE THE SECOND NUMBER
    temp.close()
    del temp

    self.game_scene = game_scene

    self.HEADER = 250
    self.PORT = 5051
    self.FORMAT = 'utf-8'
    self.DISCONNECT_MESSAGE = "!DISCONNECT"
    self.SERVER = rules.server

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
    try:
      self.game_scene.process_instructions(recieved_data)
      recieved_data = self.client.recv(4096) # large header for initial game loading
      self.game_scene.process_instructions(recieved_data)
    except:
      pass
    self.handle_active_server_data()
    return
    
  def handle_active_server_data(self):
    while True:
      recieved_data = self.client.recv(self.HEADER)

      disconnect = self.game_scene.process_instructions(recieved_data)
      if disconnect:
        self.disconnect()
        return