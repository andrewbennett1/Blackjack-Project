from errno import EDEADLK
import socket 
import threading
import random
import pickle
import time
import pygame



import sys

"""
ServerHost:
  Handles relationship between the host and clients.
  Primarily transmits and recieves data.

GameComponents:
  Holds all components in the game.
  Used when a new client joins the game so they can download
    the map and entities to their machine.


Other:
  These Classes are data to be sent to clients using pickle
  These are essentially used as commands clients will process

"""



"""
# Server class should have a main body which constantly listens, instead of 



"""

class ServerHost:

  def __init__(self, game_manager):
    self.game_manager = game_manager

    # Getting the local IP of the computer can be weird  
    try:
      SERVER = socket.gethostbyname(socket.gethostname())
    except:
      temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      temp.connect(("8.8.8.8", 80))
      SERVER = temp.getsockname()[0]
      temp.close()
      del temp
      
      


    self.HEADER = 150
    self.PORT = 5051
    self.ADDR = (SERVER, self.PORT)
    self.SERVER = SERVER
    self.FORMAT = 'utf-8'
    self.DISCONNECT_MESSAGE = "!DISCONNECT"

    self.connections = {}

    # key is the long one (conn), value is the shorter id (addr)

    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: # remove this later
      self.server.bind(self.ADDR)
    except:
      print('Address already in use')
      exit()

    self.game_components = GameComponents()
    self.game_components.temp()



  def handle_client(self, conn, addr, HEADER, FORMAT, DISCONNECT_MESSAGE):
    print(f"[NEW CONNECTION] {addr} connected.")
    self.game_components.create_new_entity(self.game_manager, addr)

    connected = True
    self.connections[conn] = addr

    # self.distribute_data_to_clients(MessageString('hello there'))
    # time.sleep(0.01) # Client can't keep up with these sometimes.


    # self.distribute_data_to_client(conn, MessageCommand(['CONNECTION', addr]))
    
    
    self.distribute_data_to_client(conn, f'cm|CONNECTION|{addr}')
    self.distribute_data_to_client(conn, self.game_components, True)
    time.sleep(0.05)
    # Updates the new client with entity positions and other data
    # self.distribute_data_to_clients(MessageCommand(['REQUEST_DATA'])) 

    # flag enable this
    self.distribute_data_to_clients('cm|REQUEST_DATA') 
    

    self.handle_active_client(connected, conn, addr, HEADER, FORMAT)
    

    # self.connections.remove(conn)
    del self.connections[conn]
    conn.close()

  # @measure_time
  def handle_active_client(self, connected, conn, addr, HEADER, FORMAT):
    while connected:
      """
      I will only be sending and recieving data as classes as they can be more easily used by the program
      
      """
      try:
        
        recieved_data = conn.recv(HEADER)
        decoded_data = recieved_data.decode(self.FORMAT)
      except:
        print('CONNECTION LOST WITH CLIENT')
        self.user_disconnected(conn)
        return
      # print('input', decoded_data)
        
      if decoded_data:
        if decoded_data[0] == 'u': # user change
          self.distribute_data_to_clients(decoded_data) # flag make this more efficient and not recode again


  def user_disconnected(self, conn): # flag add a new dict with player: entityID
    if conn in self.connections.keys():
      del self.connections[conn]

    # entityID = self.game_manager.gameScene.player_character.entityID
    try:
      for entity in self.game_components.entities:
        if conn.getpeername() == entity.owner:
          entityID = entity.entityID
          self.game_components.make_entity_inactive(entity)
          break
      self.game_manager.client.send(f'u|{entityID}|re')
    except:
      pass
        
    # self.game_manager.client.send(MessageUpdateEntity(entityID, 'remove_entity', []))
    # self.game_manager.client.send(f'u|{entityID}|re')
    
    

    

    # for i in self.game_manager.scene_manage.gameScene



  def start(self):
    server = self.server

    server.listen()
    print(f"[LISTENING] Server is listening on {self.SERVER}")
    while True:
      # Waits for another client to join. Then creates a thread for each client.
      try: 
        conn, addr = server.accept()
      except ConnectionAbortedError: # Error raises when the server is closed by the host.
        print('Server quit')

        return
      thread = threading.Thread(target=self.handle_client, 
      args=(conn, addr, self.HEADER, self.FORMAT, self.DISCONNECT_MESSAGE), daemon=True)
      thread.start()
      # print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

  # @measure_time
  def distribute_data_to_clients(self, data='', pickle_input=False): # this isnt working
    time.sleep(0.0001) # Sending messages too quickly can cause them to become lost
    for conn in self.connections.keys():

      if pickle_input:
        encoded_data = pickle.dumps(data)

      else:
        encoded_data = data.encode(self.FORMAT)
      if sys.getsizeof(encoded_data) >= self.HEADER and pickle_input==False:
        print('WARNING ---------- HEADER TOO SMALL ----------', sys.getsizeof(encoded_data))
      conn.send(encoded_data)

  # @measure_time
  def distribute_data_to_client(self, conn, data='', pickle_input=False): # this isnt working
    time.sleep(0.0001) # Sending messages too quickly can cause them to become lost
    

    if pickle_input:
        encoded_data = pickle.dumps(data)
    else:
      encoded_data = data.encode(self.FORMAT)
    if sys.getsizeof(encoded_data) >= self.HEADER and pickle_input==False:
      print('WARNING ---------- HEADER TOO SMALL ----------', sys.getsizeof(encoded_data))
    conn.send(encoded_data)
  


  def end(self): # This closes the socket
    # self.distribute_data_to_clients(MessageCommand(['HOST_DISCONNECT']))
    self.distribute_data_to_clients('cm|HOST_DISCONNECT')
    time.sleep(0.1)
    
    self.server.close()

class GameComponents:
  def __init__(self):

    self.inactive_entities = []

    self.entities = []
    self.static_components = []

    self.entityIDIncrement = 0
  
  def temp(self):
    self.static_components.append(pygame.Rect(300,300,100,50))


  def make_entity_inactive(self, entity): # account names will allow people to rejoin their inactive account

    self.entities.remove(entity)
    self.inactive_entities.append(entity)

    # print('<<<<< running')

    # entityID = self.player_character.entityID
    # self.game_manager.client.send(
    #   MessageUpdateEntity(entityID, 'remove_entity', []))
    


  def create_new_entity(self, game_manager, owner=None):
    # This class is used to store a character for initial loading
    

    # def __init__(self, entityID, entity_type, pos, username=None, owner=None):

    pos = (random.randrange(100,500), random.randrange(100,500))
    color = (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))

    # newCharacterClass = MessageCharacter('uhh', self.entityIDIncrement, pos, color, owner)
    # newCharacterClass = MessageCharacter(self.entityIDIncrement, entity_type, pos, username, owner)

    # newCharacterClass = MessageCharacter(self.entityIDIncrement, color, pos, 'lol', owner)

    newCharacterString = f'ch|{self.entityIDIncrement}|{color}|{pos}|lol|{owner}'
    # flag this looks like it is sending twice


    # self.entities.append(newCharacterClass)
    game_manager.server.distribute_data_to_clients(newCharacterString)

    self.entityIDIncrement += 1

    


