import pygame
import random
from os import system, name
import time
from classes import Dealer, User, Bot, Card, Button, TextLabel
import sys
from threading import Thread
import socket
from server import ServerHost
from client import Client
from scene_manager import GameScene, StartScene





pygame.init()
screen = pygame.display.set_mode((900, 600), pygame.RESIZABLE)
pygame.display.set_caption('Blackjack')
pygame.display.set_icon(pygame.transform.scale(pygame.image.load(f'images/back.png').convert_alpha(), (200, 200)))
clock = pygame.time.Clock()




felt = pygame.transform.scale(pygame.image.load(f'images/felt.png').convert_alpha(), (screen.get_size()))


def clear(): 
    _ = system('clear')
  

# button = Button((100,100), (100,200), 'test.png', 'test2.png', test_func)


class GameManager:
  def __init__(self):
    self.start_scene = StartScene(self)
    self.game_scene = None

    
    self.current_scene = self.start_scene
    self.previous_screen_size = screen.get_size()


  
  def process_game_iteration(self):
    cursor_pos = pygame.mouse.get_pos()





    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

      if event.type == pygame.KEYDOWN:
        if event.unicode == '|':
          pass

      if event.type == pygame.MOUSEBUTTONDOWN:

        if pygame.mouse.get_pressed()[0]:
          self.current_scene.handle_left_click(cursor_pos)
      

      
      if event.type == pygame.VIDEORESIZE:
        global felt
        width, height = event.size
        if width < 600:
            width = 600
        if height < 400:
            height = 400
        screen = pygame.display.set_mode((width,height), pygame.RESIZABLE)
        felt = pygame.transform.scale(pygame.image.load(f'images/felt.png').convert_alpha(), (width, height))

        self.current_scene.resizeScreenElements(screen)


    self.current_scene.run_actions()

    self.draw_screen(cursor_pos)
    



  def draw_screen(self, cursor_pos):
    self.current_scene.draw(cursor_pos, screen, felt)




  def startHost(self):
    self.isHost = True
    # Creates the server on a thread. This code will be moved later and user can choose to host.
    self.server = ServerHost(self)
    self.serverHostThread = Thread(target=self.server.start, args=())
    self.serverHostThread.start()




    # this will be moved later
    self.active_scene.temp() # creates the send packet button.
    self.scene_manager.change_to_game_scene()
    # self.active_scene = self.scene_manager.active_scene

  def endHost(self):



    self.server.end()
    self.isHost = False
  
  def startClient(self):
    try: # try to connect to the host
      client = Client(self)
      client_loader = client.client_loader
    except ConnectionRefusedError:
      print('Unable to connect to host')
      return
    except socket.gaierror:
        print('Invalid IP')
        return

    self.client_loader = client_loader
    self.client = client

    self.client.send('connected : )')

    self.isClient = True

    # this will be moved later
    self.scene_manager.change_to_game_scene()
    # self.active_scene = self.scene_manager.active_scene
    

  def endClient(self):
    self.client.send('!DISCONNECT')
    self.isClient = False


  def start_game_singleplayer(self):
    print('starting')
    self.game_scene = GameScene(self, False)
    self.current_scene = self.game_scene
    self.current_scene.resizeScreenElements(screen)
    

  def start_game_multiplayer(self):
    print('starting')
    self.game_scene = GameScene(self, True)
    self.current_scene = self.game_scene
    self.current_scene.resizeScreenElements(screen)

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


      # """ Each player gets a turn """
      # for player in self.players: # each player should play
      #   player.active = True

      #   #Players handle all of their actions by themselves, including drawing cards
      #   print('NEXT:', player)
      #   exit()
      #   player.make_action(self.players)


      """ Calculate winners"""
      print("DONE")
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
  game = GameManager()
  game.current_scene.resizeScreenElements(screen)
  while True:
    # screen.fill((80,85,80))
    # game.current_scene.resizeScreenElements(screen)
    game.process_game_iteration()

    # game.begin_game()

    pygame.display.update()
    clock.tick(60)

# def begin_game()

