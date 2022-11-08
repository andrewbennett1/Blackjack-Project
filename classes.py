import pygame

class Hand:
  def __init__(self):
    self.cards = []
  

class Player:
  def __init__(self, chips, name, player_id):
    self.hands = [Hand()]
    self.active_hand = self.hands[0] # splitting requires multiple hands.
    # ^^ Could also be an interesting game modifier for a custom game.
    self.name = name
    self.player_id = player_id
  
    self.chips = chips # will be set to the default 
    self.bet = None # Int of the bet a player has placed.
    self.eliminated = False # true when player is eliminated from the round
    self.active = False # if the player is currently having its turn

    if player_id == 0: # top 
      self.default_card_pos = (25,0)
      self.card_move_direction = (7,0)
      self.card_rotation = 0
    elif player_id == 1: # bottom
      self.default_card_pos = (25,70)
      self.card_move_direction = (7,0)
      self.card_rotation = 0
    elif player_id == 2: # left
      self.default_card_pos = (0,20)
      self.card_move_direction = (0,10)
      self.card_rotation = 270
    elif player_id == 3: # right
      self.default_card_pos = (80,60)
      self.card_move_direction = (0,-10)
      self.card_rotation = 90

    



  def position_hand_cards(self):
    # pos_x = 0.1
    pos_x, pos_y = self.default_card_pos

    for card in self.active_hand.cards:
      # card.pos_percent[0] = pos_x
      card.pos_percent = (pos_x, pos_y)
      pos_x += self.card_move_direction[0]
      pos_y += self.card_move_direction[1]
    


  
  def calculate_result(self, to_beat):
    value = self.calculate_hand()
    if self.eliminated or value > 21: # player eliminated
      return 'lose'
    elif to_beat > 21: # dealer bust and player not bust
      return 'win'
    elif value > to_beat: # player higher then dealer
      return 'win'
    elif value == to_beat: # player equals dealer
      return 'tie'
    elif value < to_beat: # player less then dealer
      return 'lose'
    else:
      print(f'Result calculation issue. Hand: {value}, Dealer: {to_beat}')
      exit()
  
  def draw_cards(self, screen):
    self.position_hand_cards()
    for card in self.active_hand.cards:
      card.resize(screen)
      card.draw(screen)

    
    



  def calculate_hand(self):
    # Calculate the value of the active hand
    # Accounts for aces and lowers accordingly.
    total = 0
    for card in self.active_hand:
      total += card.value
    
    if total > 21:
      for card in self.active_hand:
        if card.is_ace and total > 21: 
          # the second check ensures the correct amount of aces are accounted for.
          total -= 10
    return total
  
  

class Bot(Player):
  def __init__(self, chips, name, player_id):
    super().__init__(chips, name, player_id)

  def make_action(self, game):
    self.active = True
    while self.active:
      value = self.calculate_hand()

      if value < 17: # hit
        self.draw_card_to_hand(game)
      elif value > 21: # bust
        self.eliminated = True
        self.active = False
      elif value >= 17: # stand
        self.active = False
  
  def place_bet(self):
    self.bet = int(self.chips * 0.1)
    self.chips -= self.bet



class Dealer(Player):
  def __init__(self, name, player_id) -> None:
    super().__init__('inf', name, player_id) # dealer has infinite chips

  def make_action(self, game):
    # add cards until the dealer has a high value.
    self.active = True
    while self.active:
      value = self.calculate_hand()
      if value < 17: # hit
        self.draw_card_to_hand(game)
      elif value > 21: # bust
        self.eliminated = True
        self.active = False
      elif value >= 17: # stand
        self.active = False


class User(Player):
  def __init__(self, chips, name, player_id):
    super().__init__(chips, name, player_id)

  def make_action(self):
    print('user would be able to select an option here')
    pass


  def place_bet(self):
    pass
    # User creates their own bet
    # In progress


class Card(pygame.sprite.Sprite):
  def __init__(self, value, suit, pos):
    super().__init__()
    self.pos_percent = pos
    self.x, self.y = pos
    self.hidden = False
    self.visible = True


    self.is_ace = False
    """ Allocate a value """
    if value == 1:
      self.is_ace = True
      self.value = 11
      self.display_value = 'A'
    elif value > 1 and value <= 10:
      self.value = value
      self.display_value = str(value)
    elif value == 11:
      self.display_value = 'J'
      self.value = 10
    elif value == 12:
      self.display_value = 'Q'
      self.value = 10
    elif value == 13:
      self.display_value = 'K'
      self.value = 10

    self.suit = suit
    if suit == '♣':
      tmp = 'clubs'
    elif suit == '♠':
      tmp = 'spades'
    elif suit == '♦':
      tmp = 'diamonds'
    elif suit == '♥':
      tmp = 'hearts'
    if self.display_value not in ('10', 'A', 'J', 'K', 'Q'):
      tmp2 = '0' + str(self.display_value)
    else: tmp2 = self.display_value

    self.img_src = pygame.image.load(f'images/card_{tmp}_{tmp2}.png').convert_alpha()
    self.back_src = pygame.image.load(f'images/back.png').convert_alpha()

    self.img = self.img_src
    self.back = self.back_src

    self.rotation = 0

    

  def resize(self, screen):
    CARD_SIZE = (10, 30)

    screen_size = screen.get_size()



    new_x, new_y = int(self.pos_percent[0] / 100 * screen_size[0]), int(self.pos_percent[1] / 100 * screen_size[1])
    new_w, new_h = int(20 / 100 * screen_size[0]), int(30 / 100 * screen_size[1])

    self.x, self.y = new_x, new_y
    self.img_display = pygame.transform.rotate(pygame.transform.scale(self.img_src, (new_w, new_h)), self.rotation)
    self.back_display = pygame.transform.rotate(pygame.transform.scale(self.back_src, (new_w, new_h)), self.rotation)



  def draw(self, screen):
    if self.visible == False: return
    # w, h = self.img.get_size()
    if self.hidden: screen.blit(self.back_display, (self.x, self.y))
    else: screen.blit(self.img_display, (self.x, self.y))
    # screen.blit(self.value_icon, (w-10, h+10))
    # screen.blit(self.suit_icon, (self.x+10, self.y+40))







class Button:
  """ The button display only supports images """

  def __init__(self, pos, size, img, hover_img, action_func):
    self.size_percent = size
    self.pos_percent = pos

    self.img_src = pygame.image.load(img).convert_alpha()
    self.hover_img_src = pygame.image.load(hover_img).convert_alpha()
      
    self.size_display = size
    self.img_display = self.img_src
    self.hover_img_display = self.hover_img_src

    self.collision_rect = self.img_display.get_rect()
    self.collision_rect.x, self.collision_rect.y = pos

    self.run_action = action_func

    self.rotation = 0
  
  def resize(self, screen):
    screen_size = screen.get_size()

    new_x, new_y = int(self.pos_percent[0] / 100 * screen_size[0]), int(self.pos_percent[1] / 100 * screen_size[1])
    self.collision_rect.x = new_x
    self.collision_rect.y = new_y
    new_w, new_h = int(self.size_percent[0] / 100 * screen_size[0]), int(self.size_percent[1] / 100 * screen_size[1])

    self.collision_rect.width = new_w
    self.collision_rect.height = new_h

    self.img_display = pygame.transform.scale(self.img_src, (new_w, new_h))
    self.hover_img_display = pygame.transform.scale(self.hover_img_src, (new_w, new_h))



  def click(self, cursor_pos):
    """ cursor_pos: (x, y) """
    if pygame.mouse.get_pressed()[0]: # Checks for a left click
      if self.collision_rect.collidepoint(cursor_pos[0], cursor_pos[1]):
        self.run_action()
    return False

  def draw(self, cursor_pos, screen):
    """ cursor_pos: (x, y), screen = pygame.Surface """
    if self.collision_rect.collidepoint(cursor_pos):
      screen.blit(self.hover_img_display, (self.collision_rect.x, self.collision_rect.y))
    else:
      screen.blit(self.img_display, (self.collision_rect.x, self.collision_rect.y))



