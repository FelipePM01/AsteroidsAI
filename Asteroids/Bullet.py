import math
import pygame
class Bullet:
    def __init__(self, x, y, direction,bullet_speed,display_height,display_width):
        self.x = x
        self.y = y
        self.dir = direction
        self.life = 30
        self.bullet_speed=bullet_speed
        self.display_height=display_height
        self.display_width=display_width

    def updateBullet(self,disable_display,gameDisplay,white):
        # Moving
        self.x += self.bullet_speed * math.cos(self.dir * math.pi / 180)
        self.y += self.bullet_speed * math.sin(self.dir * math.pi / 180)

        # Drawing
        if not disable_display:
            pygame.draw.circle(gameDisplay, white, (int(self.x), int(self.y)), 3)

        # Wrapping
        if self.x > self.display_width:
            self.x = 0
        elif self.x < 0:
            self.x = self.display_width
        elif self.y > self.display_height:
            self.y = 0
        elif self.y < 0:
            self.y = self.display_height
        self.life -= 1