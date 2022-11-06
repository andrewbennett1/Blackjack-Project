import pygame
import random
from os import system, name
import time
from classes import Dealer, User, Bot, Card
import sys


"""
TODO

get sprites
position cards and chips
make chip system
finish player and dealer ai



"""


pygame.init()
screen = pygame.display.set_mode((900, 600), pygame.RESIZABLE)
pygame.display.set_caption('Blackjack')
# pygame.display.set_icon('Blackjack')
clock = pygame.time.Clock()


DECK_POS = (600, 400)




def clear(): 
    _ = system('clear')


  
  

class Game:
  def __init__(self, ai_players_num, starting_chip_num, deck_num, deck_shuffle_frequency):

    self.player_character = User(starting_chip_num, 'You')
    self.dealer = Dealer('Dealer')
    self.players = [self.dealer, self.player_character]
    self.active_player = self.players[1] # don't start at dealer
    self.game_status = None

    iteration = 0
    for i in range(ai_players_num):
      iteration += 1
      self.players.append(Bot(starting_chip_num, f'Bot-{iteration}'))

    

    # self.starting_chip_num = starting_chip_num

    self.deck = self.create_deck(deck_num)
    # self.discarded = []



    # self.deck_shuffle_frequency = deck_shuffle_frequency
  
  
  def process_game_iteration(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

      if event.type == pygame.KEYDOWN:
        if event.unicode == '|':
          pass
    


    # if self.game_status == 'player_turn':
    #   self.display_player_options()

    if self.player_character.active: # player is making their turn
      pass

    else: # Bots do their own thing
      pass


    self.draw_screen()
    
  def draw_screen(self):
    for i in self.deck:
      i.draw(screen)
      # i.font.render(i.display_value, True, (255,255,255), (0,0,0))
      screen.blit(i.tmp_text,(i.x,i.y))
    
    if self.active_player == self.player_character: # Display player buttons
      pass



  def create_deck(self, deck_num):
    deck = []
    for i in range(deck_num):
      for suit in ('♠', '♣', '♦', '♥'):
        for number in range(13):
          deck.append(Card(number+1, suit))
    random.shuffle(deck)
    return deck
  
  def draw_card(self):
    # player.hand.append(self.deck.pop())
    return self.deck.pop()
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
      


  def begin_game(self):
    

    while True: # keep playing more rounds
      # Reset from previous round
      self.reset_game()

      """ Players place a bet"""
      for player in self.players:
        player.place_bet()
      """ Need to wait here for the player to place a bet """


      # Deal two cards to everyone
      for player in self.players:
        self.draw_card(player, False)
      for player in self.players:
        if player.is_dealer: # dealer only starts with one card
          continue
        self.draw_card(player)


      """ Each player gets a turn """
      for player in self.players: # each player should play
        player.active = True

        #Players handle all of their actions by themselves, including drawing cards
        player.make_action(self.players)


      """ Calculate winners"""
      dealer_num = self.dealer.calculate_hand()
      for player in self.players:
        outcome = player.calculate_result(dealer_num) # Gets outcome of round from player

        if outcome == 'win':
          player.chips += 2 * player.bet
        elif outcome == 'tie':
          player.chips += player.bet
        elif outcome == 'lose':
          pass


    









# deck = create_deck()
# random.shuffle(deck)

# for i in deck:
  # print(i.display_icon, i.suit)


# def process_game_iteration():
  





if __name__ == "__main__":
  # run_game()
  game = Game(1, 300, 1, 1)
  while True:
    screen.fill((80,85,80))
    game.process_game_iteration()

    # game.begin_game()

    pygame.display.update()
    clock.tick(60)

# def begin_game()

