from errno import EDEADLK
import socket 
import threading
import random
import pickle
import time
import pygame
import sys


class ServerHost:

  def __init__(self, game_manager):
    self.success = False
    self.game_manager = game_manager

    try:
      SERVER = socket.gethostbyname(socket.gethostname())
    except:
      temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      temp.connect(("8.8.8.8", 80))
      SERVER = temp.getsockname()[0]
      temp.close()
      del temp
      
      
    print('server starting', SERVER)

    self.HEADER = 250
    self.PORT = 5051
    self.ADDR = (SERVER, self.PORT)
    self.SERVER = SERVER
    self.FORMAT = 'utf-8'
    self.DISCONNECT_MESSAGE = "!DISCONNECT"

    self.connections = {}

    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: # remove this later
      self.server.bind(self.ADDR)
    except:
      print('Address already in use. Please wait.')
      return

    self.success = True


  def handle_client(self, conn, addr, HEADER, FORMAT, DISCONNECT_MESSAGE):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    self.connections[conn] = addr

    self.distribute_data_to_client(conn, f'cm|CONFIRM|{addr}')

    self.distribute_data_to_clients(f'cm|NEW_PLAYER|{addr}')

    for player in self.connections:
      self.distribute_data_to_client(conn, f'cm|CONNECTION|{self.connections[player]}')

    time.sleep(0.05)
    self.handle_active_client(connected, conn, addr, HEADER, FORMAT)

    del self.connections[conn]
    conn.close()

  # @measure_time
  def handle_active_client(self, connected, conn, addr, HEADER, FORMAT):
    while connected:
      try:
        
        recieved_data = conn.recv(HEADER)
        decoded_data = recieved_data.decode(self.FORMAT)
        if decoded_data: print('server recieve:', decoded_data)
      except:
        print('CONNECTION LOST WITH CLIENT')
        self.user_disconnected(conn)
        return

      if decoded_data:
        decoded_data = decoded_data.split('&')

        for i in decoded_data:
        

          if i == 'pickup_card': # user change
            new_card = self.game_manager.deck.pop()

            time.sleep(0.01) # Properly que the sending because why not it fixes something.
            self.distribute_data_to_clients(f'c|{conn.getpeername()}|{new_card.value}|{new_card.suit}|{new_card.pos_percent}') # flag make this more efficient and not recode again
          if i == 'dealer_pickup_card': # user change
            new_card = self.game_manager.deck.pop()
            self.distribute_data_to_clients(f'dc|{new_card.value}|{new_card.suit}|{new_card.pos_percent}') # flag make this more efficient and not recode again
          if i == 'cm|NEW_ROUND':
            self.distribute_data_to_clients('cm|NEW_ROUND|')
            print(self.game_manager.player_turn_order, 'nah4')
            try: # if is ClientPlayer
              self.distribute_data_to_clients(f'np|{self.game_manager.player_turn_order[0].client_info}|')
            except:

              self.distribute_data_to_clients(f'np|{self.game_manager.client.client.getsockname()}|')
          if i == 'next_player':
            current = self.game_manager.player_turn_order.index(self.game_manager.active_player)
            current += 1
            try:
              self.active_player = self.player_turn_order[current]
              self.distribute_data_to_clients(f'np|{self.active_player.getpeername()}|')
            except:
              self.distribute_data_to_clients(f'cm|winner|')
            if self.game_manager.active_player == self.game_manager.dealer:
              self.game_manager.dealer.make_action()


  def user_disconnected(self, conn): # flag add a new dict with player: entityID
    if conn in self.connections.keys():
      del self.connections[conn]

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

  def distribute_data_to_clients(self, data='', pickle_input=False): # this isnt working
    time.sleep(0.0001) # Sending messages too quickly can cause them to become lost
    print('server sends:', data, len(self.connections))
    data = data + '&'
    for conn in self.connections.keys():

      if pickle_input:
        encoded_data = pickle.dumps(data)

      else:
        encoded_data = data.encode(self.FORMAT)
      if sys.getsizeof(encoded_data) >= self.HEADER and pickle_input==False:
        print('WARNING ---------- HEADER TOO SMALL ----------', sys.getsizeof(encoded_data))
      conn.send(encoded_data)


  def distribute_data_to_client(self, conn, data='', pickle_input=False): # this isnt working
    time.sleep(0.0001) # Sending messages too quickly can cause them to become lost
    print('server send:', data, conn)
    data = data + '&'
    if pickle_input:
        encoded_data = pickle.dumps(data)
    else:
      encoded_data = data.encode(self.FORMAT)
    if sys.getsizeof(encoded_data) >= self.HEADER and pickle_input==False:
      print('WARNING ---------- HEADER TOO SMALL ----------', sys.getsizeof(encoded_data))
    conn.send(encoded_data)
  
  def end(self): # This closes the socket
    print('ended')
    self.distribute_data_to_clients('cm|HOST_DISCONNECT')
    time.sleep(0.1)
    
    self.server.close()