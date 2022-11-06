import pygame

class Hand:
  def __init__(self):
    self.cards = []

class Player:
  def __init__(self, chips, name):
    self.hands = [Hand()]
    self.active_hand = self.hands[0] # splitting requires multiple hands.
    # ^^ Could also be an interesting game modifier for a custom game.
    self.name = name
  
    self.chips = chips # will be set to the default 
    self.bet = None # Int of the bet a player has placed.
    self.eliminated = False # true when player is eliminated from the round
    self.active = False # if the player is currently having its turn

  def draw_card_to_hand(self, game):
    card = game.draw_card()
    self.active_hand.cards.append(card)
  
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
  def __init__(self, chips, name):
    super().__init__(chips, name)

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
  def __init__(self, name) -> None:
    super().__init__('inf', name) # dealer has infinite chips

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
  def __init__(self, chips, name):
    super().__init__(chips, name)

  def make_action(self):
    print('user would be able to select an option here')
    pass


  def place_bet(self):
    pass
    # User creates their own bet
    # In progress


class Card(pygame.sprite.Sprite):
  def __init__(self, value, suit):

    super().__init__()
    
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
    self.img = pygame.transform.scale(pygame.image.load('images/card_temp.png').convert_alpha(), (200, 200))

    self.x = 100
    self.y = 100

    self.tmp_text = pygame.font.Font(f"Bold.ttf", 20).render(self.display_value, True, (255,255,255), (0,0,0))

    self.is_ace = False

    self.value_icon = pygame.font.Font(f"Bold.ttf", 20).render(self.display_value, True, (255,0,0), (255,255,255))
    self.suit_icon = pygame.font.Font(f"Bold.ttf", 200).render(self.suit, True, (255,0,0), (255,255,255))



  def draw(self, screen):
    w, h = self.img.get_size()
    screen.blit(self.img, (self.x, self.y))
    screen.blit(self.value_icon, (w-10, h+10))
    screen.blit(self.suit_icon, (self.x+10, self.y+40))
