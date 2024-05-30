import pygame
import math
import random

from Asteroids.Asteroids import Player, Saucer

class Game:
    def __init__(self,fps,model_playing,disable_display) -> None:
        pygame.init()
        #init run constants
        self.fps=fps
        self.model_playing=model_playing
        self.disable_display=disable_display
        
        #init game constants
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.black = (0, 0, 0)

        self.display_width = 800
        self.display_height = 600

        self.player_size = 10
        self.fd_fric = 0.5
        self.bd_fric = 0.1
        self.player_max_speed = 20
        self.player_max_rtspd = 10
        self.bullet_speed = 15
        self.saucer_speed = 5
        self.small_saucer_accuracy = 10 

        #init surface and display
        self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption("Asteroids")
        self.timer = pygame.time.Clock()

        #init sound effects

        self.snd_fire = pygame.mixer.Sound("Sounds/fire.wav")
        self.snd_bangL = pygame.mixer.Sound("Sounds/bangLarge.wav")
        self.snd_bangM = pygame.mixer.Sound("Sounds/bangMedium.wav")
        self.snd_bangS = pygame.mixer.Sound("Sounds/bangSmall.wav")
        self.snd_extra = pygame.mixer.Sound("Sounds/extra.wav")
        
    def start_game_loop(self):
        self.gameState = 0
        self.playerState = 0
        self.player_pieces = 0
        self.player_dying_delay = 0
        self.player_invi_dur = 0
        self.hyperspace = 0
        self.next_level_delay = 0
        self.bullet_capacity = 4
        self.bullets = []
        self.asteroids = []
        self.stage = 3
        self.score = 0
        self.live = 0
        self.oneUp_multiplier = 1
        self.playOneUpSFX = 0
        self.intensity = 0

        self.player = Player(self.display_width / 2, self.display_height / 2, self.player_max_speed, self.player_max_rtspd, self.fd_fric, self.bd_fric, self.player_size, self.display_width, self.display_height)
        self.saucer = Saucer()

        while self.gameState == 0:
            self.playStep()

    def CloseGame():
        pygame.quit()
        quit()

    def playSound(self,*args):
        if self.disable_display:
            return
        pygame.mixer.Sound.play(*args)

    def gameDisplayFill(self,color):
        if self.disable_display:
            return
        self.gameDisplay.fill(color)

    def pygameDisplayUpdate(self):
        if self.disable_display:
            return
        pygame.display.update()

        
    # Create function to draw texts
    def drawText(self,msg, color, x, y, s, center=True):
        if self.disable_display:
            return
        screen_text = pygame.font.SysFont("Calibri", s).render(msg, True, color)
        if center:
            rect = screen_text.get_rect()
            rect.center = (x, y)
        else:
            rect = (x, y)
        self.gameDisplay.blit(screen_text, rect)


    # Create funtion to chek for collision
    def isColliding(self,x, y, xTo, yTo, size):
        if x > xTo - size and x < xTo + size and y > yTo - size and y < yTo + size:
            return True
        return False




            
