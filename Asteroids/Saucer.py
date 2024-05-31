import math
import random
import pygame
import Bullet
class Saucer:
    def __init__(self,saucer_speed,display_width,display_height,disable_display):
        self.x = 0
        self.y = 0
        self.state = "Dead"
        self.type = "Large"
        self.dirchoice = ()
        self.bullets = []
        self.cd = 0
        self.bdir = 0
        self.soundDelay = 0
        self.snd_saucerB = pygame.mixer.Sound("Sounds/saucerBig.wav")
        self.snd_saucerS = pygame.mixer.Sound("Sounds/saucerSmall.wav")
        self.saucer_speed=saucer_speed
        self.display_width=display_width
        self.display_height=display_height
        self.disable_display=disable_display


        

    def updateSaucer(self):
        # Move player
        self.x += self.saucer_speed * math.cos(self.dir * math.pi / 180)
        self.y += self.saucer_speed * math.sin(self.dir * math.pi / 180)

        # Choose random direction
        if random.randrange(0, 100) == 1:
            self.dir = random.choice(self.dirchoice)

        # Wrapping
        if self.y < 0:
            self.y = self.display_height
        elif self.y > self.display_height:
            self.y = 0
        if self.x < 0 or self.x > self.display_width:
            self.state = "Dead"

        # Shooting
        if self.type == "Large":
            self.bdir = random.randint(0, 360)
        if self.cd == 0:
            self.bullets.append(Bullet(self.x, self.y, self.bdir))
            self.cd = 30
        else:
            self.cd -= 1

        # Play SFX
        if self.type == "Large":
            self.playSound(self.snd_saucerB)
        else:
            self.playSound(self.snd_saucerS)

    def createSaucer(self):
        # Create saucer
        # Set state
        self.state = "Alive"

        # Set random position
        self.x = random.choice((0, self.display_width))
        self.y = random.randint(0, self.display_height)

        # Set random type
        if random.randint(0, 1) == 0:
            self.type = "Large"
            self.size = 20
        else:
            self.type = "Small"
            self.size = 10

        # Create random direction
        if self.x == 0:
            self.dir = 0
            self.dirchoice = (0, 45, -45)
        else:
            self.dir = 180
            self.dirchoice = (180, 135, -135)

        # Reset bullet cooldown
        self.cd = 0

    def drawSaucer(self,gameDisplay,white):
        # Draw saucer
        if self.disable_display:
            return
        pygame.draw.polygon(gameDisplay, white,
                            ((self.x + self.size, self.y),
                             (self.x + self.size / 2, self.y + self.size / 3),
                             (self.x - self.size / 2, self.y + self.size / 3),
                             (self.x - self.size, self.y),
                             (self.x - self.size / 2, self.y - self.size / 3),
                             (self.x + self.size / 2, self.y - self.size / 3)), 1)
        pygame.draw.line(gameDisplay, white,
                         (self.x - self.size, self.y),
                         (self.x + self.size, self.y))
        pygame.draw.polygon(gameDisplay, white,
                            ((self.x - self.size / 2, self.y - self.size / 3),
                             (self.x - self.size / 3, self.y - 2 * self.size / 3),
                             (self.x + self.size / 3, self.y - 2 * self.size / 3),
                             (self.x + self.size / 2, self.y - self.size / 3)), 1)

    def playSound(self,*args):
        if self.disable_display:
            return
        pygame.mixer.Sound.play(*args)