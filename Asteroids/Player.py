import math
import pygame
class Player:
    def __init__(self, x, y,max_speed,max_rtspd,fd_fric,bd_fric,size,display_width,display_height):
        self.x = x
        self.y = y
        self.hspeed = 0
        self.vspeed = 0
        self.dir = -90
        self.rtspd = 0
        self.thrust = False
        self.max_speed=max_speed
        self.max_rtspd=max_rtspd
        self.fd_fric=fd_fric
        self.bd_fric=bd_fric
        self.size=size
        self.display_width=display_width
        self.display_height=display_height

    def updatePlayer(self):
        # Move player
        speed = math.sqrt(self.hspeed**2 + self.vspeed**2)
        if self.thrust:
            if speed + self.fd_fric < self.max_speed:
                self.hspeed += self.fd_fric * math.cos(self.dir * math.pi / 180)
                self.vspeed += self.fd_fric * math.sin(self.dir * math.pi / 180)
            else:
                self.hspeed = self.max_speed * math.cos(self.dir * math.pi / 180)
                self.vspeed = self.max_speed * math.sin(self.dir * math.pi / 180)
        else:
            if speed - self.bd_fric > 0:
                change_in_hspeed = (self.bd_fric * math.cos(self.vspeed / self.hspeed))
                change_in_vspeed = (self.bd_fric * math.sin(self.vspeed / self.hspeed))
                if self.hspeed != 0:
                    if change_in_hspeed / abs(change_in_hspeed) == self.hspeed / abs(self.hspeed):
                        self.hspeed -= change_in_hspeed
                    else:
                        self.hspeed += change_in_hspeed
                if self.vspeed != 0:
                    if change_in_vspeed / abs(change_in_vspeed) == self.vspeed / abs(self.vspeed):
                        self.vspeed -= change_in_vspeed
                    else:
                        self.vspeed += change_in_vspeed
            else:
                self.hspeed = 0
                self.vspeed = 0
        self.x += self.hspeed
        self.y += self.vspeed

        # Check for wrapping
        if self.x > self.display_width:
            self.x = 0
        elif self.x < 0:
            self.x = self.display_width
        elif self.y > self.display_height:
            self.y = 0
        elif self.y < 0:
            self.y = self.display_height

        # Rotate player
        self.dir += self.rtspd

    def drawPlayer(self,gameDisplay,disable_display,white):
        if disable_display:
            return
        a = math.radians(self.dir)
        x = self.x
        y = self.y
        s = self.size
        t = self.thrust
        # Draw player
        pygame.draw.line(gameDisplay, white,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) + a),
                          y - (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) + a)),
                         (x + s * math.cos(a), y + s * math.sin(a)))

        pygame.draw.line(gameDisplay, white,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) - a),
                          y + (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) - a)),
                         (x + s * math.cos(a), y + s * math.sin(a)))

        pygame.draw.line(gameDisplay, white,
                         (x - (s * math.sqrt(2) / 2) * math.cos(a + math.pi / 4),
                          y - (s * math.sqrt(2) / 2) * math.sin(a + math.pi / 4)),
                         (x - (s * math.sqrt(2) / 2) * math.cos(-a + math.pi / 4),
                          y + (s * math.sqrt(2) / 2) * math.sin(-a + math.pi / 4)))
        if t:
            pygame.draw.line(gameDisplay, white,
                             (x - s * math.cos(a),
                              y - s * math.sin(a)),
                             (x - (s * math.sqrt(5) / 4) * math.cos(a + math.pi / 6),
                              y - (s * math.sqrt(5) / 4) * math.sin(a + math.pi / 6)))
            pygame.draw.line(gameDisplay, white,
                             (x - s * math.cos(-a),
                              y + s * math.sin(-a)),
                             (x - (s * math.sqrt(5) / 4) * math.cos(-a + math.pi / 6),
                              y + (s * math.sqrt(5) / 4) * math.sin(-a + math.pi / 6)))

    def killPlayer(self):
        # Reset the player
        self.x = self.display_width / 2
        self.y = self.display_height / 2
        self.thrust = False
        self.dir = -90
        self.hspeed = 0
        self.vspeed = 0