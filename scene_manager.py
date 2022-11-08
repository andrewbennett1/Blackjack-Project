from classes import Button, Card, Dealer, User, Bot
import pygame
import random
import threading





positions = {
  0: (200,300),  # top
  1: (300,300),  # bottom
  2: (400,300), # right
  3: (500,300)   # left
}

"""
StartScene 
  Displays buttons to join or host a game
"""

class StartScene:
  def __init__(self, game_manager) -> None:
    # Create components of the scene
    self.game_manager = game_manager

    self.buttons = []
    self.static_components = []

    self.buttons.append(Button((5,20), (50, 10), 'images/singleplayer.png', 'images/singleplayer2.png', game_manager.start_game_singleplayer))
    self.buttons.append(Button((5,40), (50, 10), 'images/multiplayer.png', 'images/multiplayer2.png', game_manager.start_game_multiplayer))
    # self.buttons.append(Button((300,300), (100, 100), 'images/hit.png', game_manager.startHost))
    # self.buttons.append(Button((500,300), (200, 200), 'images/stand.png', game_manager.startClient))
    # hit_button = Button((100,100), (200,100), 'images/hit.png', 'images/hit2.png', test_func)
    # stand_button = Button((400,100), (300,100), 'images/stand.png', 'images/stand2.png', test_func)


  def resizeScreenElements(self, screen):
    for button in self.buttons:
      button.resize(screen)

  def handle_left_click(self, cursor_pos):
    for button in self.buttons:
      button.click(cursor_pos)


  def draw(self, cursor_pos, screen):
    screen.fill((80,85,80))

    for i in self.buttons:
      i.draw(cursor_pos, screen)










"""
GameScene 
  Displays and runs the game
  Creates a new GameScene for every game you join
"""

def test_func():
  print('test')

class GameScene:
  def __init__(self, game_manager, is_multiplayer):
    # Create components of the scene

    starting_chip_num = 100
    ai_players_num = 2
    deck_num = 1


    hit_button = Button((30,60), (13,8), 'images/hit.png', 'images/hit2.png', self.pickup_card)
    stand_button = Button((45,60), (20,8), 'images/stand.png', 'images/stand2.png', test_func)
    self.buttons = [hit_button, stand_button]


    self.players = []

    self.dealer = Dealer('Dealer', len(self.players))
    self.players.append(self.dealer)
    self.player_character = User(starting_chip_num, 'You', len(self.players))
    self.players.append(self.player_character)
    self.active_player = self.players[1] # don't start at dealer
    self.game_status = None


    iteration = 0
    for i in range(ai_players_num):
      iteration += 1
      self.players.append(Bot(starting_chip_num, f'Bot-{iteration}', len(self.players)))

    

    # self.starting_chip_num = starting_chip_num

    self.deck = self.create_deck(deck_num)
    self.displayed_cards = []
    self.discarded = []


    self.deck_card = Card(2, '♠', (30, 30))
    # self.deck_card.x, self.deck_card.y = , 400
    self.deck_card.hidden, self.deck_card.visible = True, True


    self.game_manager = game_manager


    for player in self.players:
      self.pickup_card(player)
      self.pickup_card(player)
      self.pickup_card(player)
      
    
    

    """
    MULTIPLAYER LOGIC BELOW
    """
    if is_multiplayer:
      pass


    # when this reaches 10, send an update to the server. Different actions change this value
    # at different rates. This stops the host being overwhelmed as I dont want my computer to
    # crash again.



    

    # self.static_components.append(pygame.Rect(300,300,100,50))

    # self.buttons.append(Button((300,300), 'server', game_manager.startHost))
    # self.buttons.append(Button((500,300), 'client', game_manager.startClient))

  # def temp(self): # using this to test sending packets via server
    # pass
    # self.buttons.append(Button((300,500), 'send', self.game_manager.server.distribute_data_to_clients))

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
  
  def pickup_card(self, player=None):
    if player == None:
      player = self.active_player
    # player.hand.append(self.deck.pop())
    card = self.deck.pop()
    card.rotation = player.card_rotation
    player.active_hand.cards.append(card)
    self.displayed_cards.append(card)
    # self.display_game()
    
    # if delay: time.sleep(0.5)
    
  
  def move_cards_to_deck(self):
    for player in self.players:
      # for card in player.hand:
        # self.deck.append(player.hand.pop())
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




  # def handle_left_click(self):
  #   for i in self.buttons:
  #     if i.click():
  #       i.action()
  def handle_left_click(self, cursor_pos):
    for button in self.buttons:
      button.click(cursor_pos)


  # @measure_time
  def update_server(self):
    # entityID = self.player_character.entityID
    # self.send_data_to_server(f'u|{entityID}|em|{(self.entities[entityID].x,self.entities[entityID].y)}')
    # self.game_manager.client.send(x)
    entityID = self.player_character.entityID
    self.send_data_to_server(f'u|{entityID}|em|{(self.entities[entityID].x,self.entities[entityID].y)}')
    # print('yeahh', f'u|{entityID}|em|{(self.entities[entityID].x,self.entities[entityID].y)}')


  # def __init__(self, entityID, command, parameter1, parameter2=None, parameter3=None): # use *args and *kwargs

  def request_data(self):
    entityID = self.player_character.entityID
    self.send_data_to_server(f'u|{entityID}|em|{(self.entities[entityID].x,self.entities[entityID].y)}')
    # # self.game_manager.client.send(MessageUpdateEntity(entityID, 'set_external_motion', [(self.entities[entityID].x, self.entities[entityID].y), True]))
    # self.game_manager.client.send(f'u|{entityID}|em|{(self.entities[entityID].x,self.entities[entityID].y)}')


  def send_data_to_server(self, data):
    # This sends data to the server. Sometimes, sockets can take a while so to reduce client
    # lag, this is a thread.

    send = threading.Thread(target=self.game_manager.client.send, args=([data]), daemon=True)
    send.start()


  # def create_component(self, component)
  # @measure_time
  def draw(self, cursor_pos, screen):
    screen.fill((80,85,80))

    self.deck_card.draw(screen)


    


    # for i in self.deck:
    #   i.draw(screen)
    
    for player in self.players:
      # player.draw_cards(positions[player.player_id], screen) flag
      player.draw_cards(screen)

      # player.active_hand.c
      # print(self.players[0].hands[0].cards[0].value)

      # i.font.render(i.display_value, True, (255,255,255), (0,0,0))
      # screen.blit(i.tmp_text,(i.x,i.y))
    # for button in self.buttons:
    #   button.draw(cursor_pos, screen)

    if self.active_player == self.player_character: # Display player buttons
      for button in self.buttons:
        button.draw(cursor_pos, screen)

  


