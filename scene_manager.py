from classes import Button, Card, Dealer, User, Bot, TextLabel, ClientPlayer
import pygame
import random
import threading
from server import ServerHost
from client import Client
from threading import Thread
import pickle
import rules
import socket
import sys
import time


positions = {
  0: (200,300),  # top
  1: (300,300),  # bottom
  2: (400,300), # right
  3: (500,300)   # left
}



class StartScene:
  def __init__(self, game_manager) -> None:
    # Create components of the scene
    self.game_manager = game_manager

    self.buttons = []
    self.static_components = []

    self.buttons.append(Button((5,20), (50, 10), 'images/singleplayer.png', 'images/singleplayer2.png', game_manager.start_game_singleplayer))
    self.buttons.append(Button((5,40), (20, 10), 'images/host.png', 'images/host2.png', game_manager.start_game_multiplayer_host))
    self.buttons.append(Button((5,55), (20, 10), 'images/join.png', 'images/join2.png', game_manager.start_game_multiplayer_client))

  def run_actions(self):
    pass

  def resizeScreenElements(self, screen):
    for button in self.buttons:
      button.resize(screen)

  def handle_left_click(self, cursor_pos):
    for button in self.buttons:
      button.click(cursor_pos)


  def draw(self, cursor_pos, screen, felt):
    # screen.fill((80,85,80))
    screen.blit(felt, (0,0))

    for i in self.buttons:
      i.draw(cursor_pos, screen)



class GameScene:
  def __init__(self, game_manager, is_multiplayer):
    # Create components of the scene
    self.is_multiplayer = is_multiplayer
    self.game_manager = game_manager
    self.isHost = False
    self.isClient = False
    self.fully_connected = False
    self.new_player_que = []

    starting_chip_num = rules.starting_chip_num
    deck_num = rules.num_of_decks
    self.text_overlay = None
    self.buttons = []
    self.toggle_buttons(False)
    self.turn_delay = 0


    """ Create Players """
    self.players = []

    self.dealer = Dealer('Dealer', [len(self.players)])
    self.players.append(self.dealer)
    self.player_character = User(rules.starting_chip_num, 'You', [len(self.players)])
    self.players.append(self.player_character)
    self.game_status = 'player_turns'

    self.deck = self.create_deck(deck_num)
    self.displayed_cards = []

    self.deck_card = Card(2, '♠', (30, 30))
    self.deck_card.hidden, self.deck_card.visible = True, True

 
    """ SINGLEPLAYER """
    if is_multiplayer[0] == False:
      ai_players_num = rules.computer_players_num

      iteration = 0
      for i in range(ai_players_num):
        iteration += 1
        self.players.append(Bot(rules.starting_chip_num, f'Bot-{iteration}', [len(self.players)]))

      """ MULTIPLAYER"""
    elif is_multiplayer[0]:
      """ Is Host """
      if is_multiplayer[1] == True: 
        self.startHost()
      """ Is Client """
      success = self.startClient()
      if not success:
        try: 
          if self.game_scene.isHost: self.endHost()
        except: pass
        pygame.quit()
        sys.exit()
      

    """ Order players """
    self.player_display_order = None
    self.set_player_positions()
    self.active_player = self.player_display_order[1] # don't start at dealer
    
    self.player_turn_order = self.player_display_order[1:]
    self.player_turn_order.append(self.player_display_order[0])


    print(self.is_multiplayer, self.isHost, self.isClient)

    " Draw starting cards "

    for player in self.players:
      self.pickup_card(player)
      if type(player) != Dealer: self.pickup_card(player)

  def startHost(self):
    # Creates the server on a thread. This code will be moved later and user can choose to host.
    self.server = ServerHost(self)
    if self.server.success == False:
      return

    self.isHost = True
    self.fully_connected = True
    self.serverHostThread = Thread(target=self.server.start, args=())
    self.serverHostThread.start()


  def startClient(self):
    try: # try to connect to the host
      client = Client(self)
    except ConnectionRefusedError:
      print('Unable to connect to host')
      return False
    except socket.gaierror:
      print('Invalid IP')
      return False
    self.client = client
    self.isClient = True
    return True

  
  def process_instructions(self, recieved_data):
    decoded_data = recieved_data.decode('utf-8')
    decoded_data_items = decoded_data.split('&')
    for i in decoded_data_items:

      decoded_data = i.split('|')
      first_item = decoded_data[0]
      print('in:', decoded_data)

      if first_item == 'cm': # COMMAND
        """ Add a new player to the game """
        if decoded_data[1] == 'CONNECTION': print(self.return_addr_from_str(decoded_data[2]) , self.client.client.getsockname(), 'uiebvw')
        if decoded_data[1] == 'CONNECTION' and self.return_addr_from_str(decoded_data[2]) != self.client.client.getsockname():
          print('new client player bruh')
          self.new_player_que.append(ClientPlayer(rules.starting_chip_num, f'Player-{len(self.players)}', [len(self.players)], self.return_addr_from_str(decoded_data[2])))

        if decoded_data[1] == 'NEW_ROUND':
          self.fully_connected = True
          self.new_round(True)
        if self.fully_connected == False:
          return
        if decoded_data[1] == 'winner':
          self.game_status = 'winner'
          self.round_end()

        if decoded_data[1] == 'NEW_PLAYER': print('GOD',self.return_addr_from_str(decoded_data[2]), self.client.client.getsockname())
        if decoded_data[1] == 'NEW_PLAYER' and self.return_addr_from_str(decoded_data[2]) != self.client.client.getsockname():
          self.new_player_que.append(ClientPlayer(rules.starting_chip_num, f'Player-{len(self.players)}', [len(self.players)], self.return_addr_from_str(decoded_data[2])))

        elif decoded_data[1] == 'HOST_DISCONNECT': # Host is disconnecting so clients must disconnect
          return True
      elif self.fully_connected == False:
        return
      elif first_item == 'c': # Card

        for player in self.players:

          if type(player) == ClientPlayer:
            if self.return_addr_from_str(decoded_data[1]) == player.client_info:

              player.hands[0].cards.append(Card(int(decoded_data[2]), decoded_data[3]))
              break

          elif type(player) == User: # The card is for the user
            if self.return_addr_from_str(decoded_data[1]) == self.client.client.getsockname():
              player.hands[0].cards.append(Card(int(decoded_data[2]), decoded_data[3]))

              if player.calculate_hand() > 21:
                self.text_overlay = TextLabel((40, 40), (20, 10), 'Bust')
                player.eliminated = True
                player.active = False
                self.stand()
              break



      elif first_item == 'dc': # dealer card
        self.dealer.hands[0].cards.append(Card(int(decoded_data[1]), decoded_data[2]))

      elif first_item == 'np': # next player
        print('lol', self.client.client.getsockname() , self.return_addr_from_str(decoded_data[1]))
        if self.client.client.getsockname() == self.return_addr_from_str(decoded_data[1]):
          self.active_player == self.player_character
          self.toggle_buttons(True)

  def return_tuple_from_string(self, string): # The values must be intended to be an int
    
    string = string.replace("'", '').replace("(", '').replace(")", '').replace(" ", '')
    string = string.split(',')
    output = []
    for i in string:
      try:
        output.append(int(i))
      except:
        return False
    string = tuple(output)
    return string
  
  def return_addr_from_str(self, string):
    conn = string
    conn = conn.replace("'", '').replace(" ", '').replace("(", '').replace(")", '')
    conn = conn.split(',')
    conn[1] = int(conn[1]) # this prob wont break anything
    conn = tuple(conn)
    return conn


  def toggle_buttons(self, on):
    if on:
      hit_button = Button((30,60), (13,8), 'images/hit.png', 'images/hit2.png', self.pickup_card)
      stand_button = Button((45,60), (20,8), 'images/stand.png', 'images/stand2.png', self.stand)
      self.buttons = [hit_button, stand_button]
    else:
      for i in self.buttons:
        del i
      self.buttons = []


  def set_player_positions(self):

    new_positions = [self.dealer, self.player_character]

    for i, player in enumerate(self.players):
      if type(player) in (Bot, ClientPlayer):
        new_positions.insert(i-1, player)
        break
    if len(new_positions) < len(self.players):
      new_positions.append(self.players[-1])
    
    self.player_display_order = new_positions

    if len(new_positions) == 2:
      self.dealer.change_card_order(0)
      self.player_character.change_card_order(2)
    else:
      for player in self.players: 
        player.change_card_order(new_positions.index(player))
    

  def run_actions(self):
    if self.is_multiplayer[0] and self.fully_connected == False:
      return

    if self.game_status == 'player_turns':

      if self.turn_delay == 0:
        if type(self.active_player) == User: self.toggle_buttons(True)

        self.active_player.make_action(self)
        self.turn_delay = 50
      else:
        self.turn_delay -= 1
    elif self.game_status == 'winner' and (self.is_multiplayer[0] == False or self.isHost == True):
      self.buttons = [Button((35,60), (30,10), 'images/again.png', 'images/again2.png', self.new_round)]
      pass
      

  def next_player(self):
    self.dealer.change_card_order(0)
    self.player_character.change_card_order(1)

    current = 2
    for i in self.players:
      if type(i) == Bot:
        i.change_card_order(current)
        current += 1

  def resizeScreenElements(self, screen):
    self.deck_card.resize(screen)
    for button in self.buttons:
      button.resize(screen)
    for card in self.displayed_cards:
      card.resize(screen)
    

  def create_deck(self, deck_num):
    deck = []
    for i in range(deck_num):
      for suit in ('♠', '♣', '♦', '♥'):
        for number in range(13):
          deck.append(Card(number+1, suit, (0,0)))
    random.shuffle(deck)
    return deck
  
  def bust(self):
    current = self.players.index(self.active_player)
    current += 1
    if current > len(self.players):
      current = 0
    self.active_player = self.players[current]

  def new_round(self, from_host=False):

    self.buttons = []
    for player in self.players:
      for hand in player.hands:
        hand.cards = []
      player.eliminated = False
    self.deck = self.create_deck(1)
    self.game_status = 'player_turns'
    self.text_overlay = None
    self.active_player = self.player_turn_order[0]
    time.sleep(0.01)

    if self.is_multiplayer[0] == False:
    

      for player in self.players:
        self.pickup_card(player)
        if type(player) != Dealer: self.pickup_card(player)
      
      

      self.new_player_que = []
    elif self.isHost and from_host == False: # dont send multiple times
      self.client.send("cm|NEW_ROUND&")
    
      for player in self.players:
        self.pickup_card(player)
        self.pickup_card(player)

    else: # multiplayer client that is not a host.
      pass


    for i in self.new_player_que:
      self.players.append(i)
      self.player_display_order = None
      self.set_player_positions()
      print(self.player_display_order, '123')
      self.player_turn_order = self.player_display_order[1:]
      self.player_turn_order.append(self.player_display_order[0])
    self.new_player_que = []


  def round_end(self):
    result = self.player_character.calculate_result(self.dealer.calculate_hand(), self.dealer)
    if result == 'lose':
      self.text_overlay = TextLabel((35, 40), (30, 10), 'You Lost')
    elif result == 'tie':
      self.text_overlay = TextLabel((35, 40), (30, 10), 'Pushback')
    elif result == 'win':
      self.text_overlay = TextLabel((35, 40), (30, 10), 'Winner!')


  def stand(self): # next player

    if self.is_multiplayer[0]:
      self.client.send("next_player&")
    else:
    
      current = self.player_turn_order.index(self.active_player)
      current += 1
      try:
        self.active_player = self.player_turn_order[current]
      except:
        # print('all players done')
        self.game_status = 'winner'
        self.round_end()


  def pickup_card(self, player=None):

    if player == None:
      player = self.active_player

    if self.is_multiplayer[0]:
      if type(player) == Dealer and self.isHost: 
        self.client.send('dealer_pickup_card&')
      else:
        self.client.send('pickup_card&') # regular player can ignore response

    else:

      # if not self.is_multiplayer: # Singleplayer or host
      card = self.deck.pop()
      card.rotation = player.card_rotation
      player.active_hand.cards.append(card)
      self.displayed_cards.append(card)

      if player == self.player_character and self.player_character.calculate_hand() > 21:
        self.text_overlay = TextLabel((40, 40), (20, 10), 'Bust')
        player.eliminated = True
        player.active = False
        self.stand()

  
  def move_cards_to_deck(self):
    for player in self.players:
      self.deck + player.active_hand
      player.hand = []


  def reset_game(self):
    self.move_cards_to_deck()
    for player in self.players:
      player.eliminated = False


  def collect_bets(self):
    for player in self.players:
      player.place_bet()


  def prime_player_character(self, conn): # Links a character with a player to be controlled

    self.game_manager.client.id
    for entity in self.entities.values():
      if entity.owner == conn:
        self.player_character = entity
        return



  def handle_left_click(self, cursor_pos):
    for button in self.buttons:
      button.click(cursor_pos)

  def update_server(self):
    entityID = self.player_character.entityID
    self.send_data_to_server(f'u|{entityID}|em|{(self.entities[entityID].x,self.entities[entityID].y)}')

  def request_data(self):
    entityID = self.player_character.entityID
    self.send_data_to_server(f'u|{entityID}|em|{(self.entities[entityID].x,self.entities[entityID].y)}')

  def send_data_to_server(self, data):
    send = threading.Thread(target=self.game_manager.client.send, args=([data]), daemon=True)
    send.start()

  def draw(self, cursor_pos, screen, felt):
    # screen.fill((80,85,80))
    screen.blit(felt, (0,0))
    
    self.deck_card.draw(screen)
    
    for player in self.players:
      player.draw_cards(screen)
      player.draw_text_labels(screen)

    if self.text_overlay != None:
      self.text_overlay.draw(screen)

    for button in self.buttons:
      button.resize(screen)
      button.draw(cursor_pos, screen)
    if self.active_player != self.player_character and self.game_status == 'player_turns': # Display player buttons
      self.toggle_buttons(False)
    
    if self.fully_connected == False and self.isClient:
      screen.blit(felt, (0,0))
      TextLabel((30, 40), (40, 10), 'Waiting for next Round').draw(screen)