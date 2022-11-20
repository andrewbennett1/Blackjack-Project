from classes import Button, Card, Dealer, User, Bot, TextLabel
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










"""
GameScene 
  Displays and runs the game
  Creates a new GameScene for every game you join
"""


class GameScene:
  def __init__(self, game_manager, is_multiplayer):
    # Create components of the scene
 
    starting_chip_num = 100
    ai_players_num = 2
    deck_num = 1

    self.text_overlay = None
    self.buttons = []

    # self.toggle_buttons(True)
    self.toggle_buttons(False)


    """ Create Players """
    self.players = []

    self.dealer = Dealer('Dealer', [len(self.players)])
    self.players.append(self.dealer)
    self.player_character = User(starting_chip_num, 'You', [len(self.players)])
    self.players.append(self.player_character)
    self.game_status = 'player_turns'


    self.turn_delay = 0

    iteration = 0
    for i in range(ai_players_num):
      iteration += 1
      self.players.append(Bot(starting_chip_num, f'Bot-{iteration}', [len(self.players)]))

    """ Order players """


    self.player_display_order = None
    self.set_player_positions()
    self.active_player = self.player_display_order[1] # don't start at dealer
    

    self.player_turn_order = self.player_display_order[1:]
    self.player_turn_order.append(self.player_display_order[0])


    

    # self.starting_chip_num = starting_chip_num

    self.deck = self.create_deck(deck_num)
    self.displayed_cards = []
    self.discarded = []


    self.deck_card = Card(2, '♠', (30, 30))
    # self.deck_card.x, self.deck_card.y = , 400
    self.deck_card.hidden, self.deck_card.visible = True, True


    self.game_manager = game_manager

    " Draw starting cards "
    for player in self.players:
      self.pickup_card(player)
      self.pickup_card(player)
    self.dealer.active_hand.cards[1].hidden = True
    # print(self.dealer.active_hand.cards)
      # self.pickup_card(player)
      
    
    

    """
    MULTIPLAYER LOGIC BELOW
    """
    if is_multiplayer:
      pass


    # when this reaches 10, send an update to the server. Different actions change this value
    # at different rates. This stops the host being overwhelmed as I dont want my computer to
    # crash again.

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
      if type(player) == Bot:
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

    if self.game_status == 'player_turns':

      if self.turn_delay == 0:
        if type(self.active_player) == User: self.toggle_buttons(True)

        self.active_player.make_action(self)
        # print('next turn', self.active_player)
        self.turn_delay = 50
      else:
        self.turn_delay -= 1
    elif self.game_status == 'winner':
      self.buttons = [Button((35,60), (30,10), 'images/hit.png', 'images/hit2.png', self.new_round)]
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

  def new_round(self):
    self.buttons = []
    for player in self.players:
      for hand in player.hands:
        hand.cards = []
      player.eliminated = False
    self.deck = self.create_deck(1)
    self.game_status = 'player_turns'

    for player in self.players:
      self.pickup_card(player)
      self.pickup_card(player)
    self.dealer.active_hand.cards[1].hidden = True
    self.text_overlay = None

    self.active_player = self.player_turn_order[0]


  def round_end(self):
    result = self.player_character.calculate_result(self.dealer.calculate_hand(), self.dealer)
    if result == 'lose':
      self.text_overlay = TextLabel((35, 40), (30, 10), 'You Lost')
    elif result == 'tie':
      self.text_overlay = TextLabel((35, 40), (30, 10), 'Pushback')
    elif result == 'win':
      self.text_overlay = TextLabel((35, 40), (30, 10), 'Winner!')


  def stand(self): # next player
    
    current = self.player_turn_order.index(self.active_player)
    # print('curr',self.active_player, current - 1)
    current += 1
    # print(self.active_player, current, len(self.players) - 1)
    try:
      self.active_player = self.player_turn_order[current]
    except:
      # print('all players done')
      self.game_status = 'winner'
      self.round_end()

      # self.text_overlay
      



      # exit()

    # if current <= len(self.players):

      # print(self.players[current - 1], current)
      # self.active_player = self.players[current - 1]
    # else:
      # print('j')
      # pass

    # if current > len(self.players) - 1:
    #   current = 0

    # flag fix this
    # print(current)
    # self.active_player = self.players[current]





  def pickup_card(self, player=None):
    if player == None:
      player = self.active_player
    # player.hand.append(self.deck.pop())


    if len(player.active_hand.cards) > 0 and player.active_hand.cards[-1].hidden == True:
      # print(self.active_player, self.active_player.active_hand.cards[-1].hidden)
      player.active_hand.cards[-1].hidden = False
      return


    card = self.deck.pop()
    card.rotation = player.card_rotation
    player.active_hand.cards.append(card)
    self.displayed_cards.append(card)

    if player == self.player_character and self.player_character.calculate_hand() > 21:
      self.text_overlay = TextLabel((40, 40), (20, 10), 'Bust')
      player.eliminated = True
      player.active = False
      self.stand()
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
  def draw(self, cursor_pos, screen, felt):
    # screen.fill((80,85,80))
    screen.blit(felt, (0,0))
    

    self.deck_card.draw(screen)
    


    


    # for i in self.deck:
    #   i.draw(screen)
    
    for player in self.players:
      # player.draw_cards(positions[player.player_id], screen) flag
      player.draw_cards(screen)
      player.draw_text_labels(screen)

    if self.text_overlay != None:
      self.text_overlay.draw(screen)

      # player.active_hand.c
      # print(self.players[0].hands[0].cards[0].value)

      # i.font.render(i.display_value, True, (255,255,255), (0,0,0))
      # screen.blit(i.tmp_text,(i.x,i.y))
    # for button in self.buttons:
    #   button.draw(cursor_pos, screen)
    # print(self.active_player)
    # print('f', self.buttons)
    for button in self.buttons:
      button.resize(screen)
      button.draw(cursor_pos, screen)
    if self.active_player != self.player_character and self.game_status == 'player_turns': # Display player buttons
      self.toggle_buttons(False)
    


  


