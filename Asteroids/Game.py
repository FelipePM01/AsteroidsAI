import pygame
import math
import random
from Player import Player
from Bullet import Bullet
from Saucer import Saucer
from Asteroid import Asteroid
from DeadPlayer import deadPlayer

class Game:
    def __init__(self,fps,model_playing,disable_display):
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

        self.snd_fire = pygame.mixer.Sound("Asteroids/Sounds/fire.wav")
        self.snd_bangL = pygame.mixer.Sound("Asteroids/Sounds/bangLarge.wav")
        self.snd_bangM = pygame.mixer.Sound("Asteroids/Sounds/bangMedium.wav")
        self.snd_bangS = pygame.mixer.Sound("Asteroids/Sounds/bangSmall.wav")
        self.snd_extra = pygame.mixer.Sound("Asteroids/Sounds/extra.wav")

        self.gameState = 0 # 0 = jogando 1 = fim de jogo
        self.playerState = 0 # 0 = vivo 1 = morto
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
        self.reward = 0

        self.player = None
        self.saucer = None
        
    def start_game_loop(self):
        self.gameState = 0 # 0 = jogando 1 = fim de jogo
        self.playerState = 0 # 0 = vivo 1 = morto
        self.player_pieces = []
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
        self.reward = 0

        self.player = Player(self.display_width / 2, self.display_height / 2, self.player_max_speed, self.player_max_rtspd, self.fd_fric, self.bd_fric, self.player_size, self.display_width, self.display_height)
        self.saucer = Saucer(self.saucer_speed, self.display_width, self.display_height, True, self.bullet_speed)

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

    def play_step(self, action):
        # Game menu
        if self.gameState == 1:
            return
        
        if action[0]==1:
            self.player.thrust=True
        else:
            self.player.thrust=False

        if action[1] == 1 and action[2] == 0:
            self.player.rtspd = self.player_max_rtspd
        elif action[2]==1 and action[1]==0:
            self.player.rtspd= -self.player_max_rtspd
        else: 
            self.player.rtspd=0
        if action[3]==1:
            self.bullets.append(Bullet(self.player.x, self.player.y, self.player.dir, self.bullet_speed, self.display_height, self.display_width))

        # Update player
        self.player.updatePlayer()

        # Checking player invincible time
        if self.player_invi_dur != 0:
            self.player_invi_dur -= 1
        elif self.hyperspace == 0:
            self.player_state = 0

        # Reset display
        self.gameDisplayFill(self.black)

        # Hyperspace
        if self.hyperspace != 0:
            self.player_state = 1
            self.hyperspace -= 1
            if self.hyperspace == 1:
                self.player.x = random.randrange(0, self.display_width)
                self.player.y = random.randrange(0, self.display_height)

        # Check for collision w/ asteroid
        for a in self.asteroids:
            a.updateAsteroid(self.display_width, self.display_height, self.gameDisplay, True, self.white)
            if self.player_state != 1:
                if self.isColliding(self.player.x, self.player.y, a.x, a.y, a.size):
                    # Create ship fragments
                    self.player_pieces.append(deadPlayer(self.player.x, self.player.y, 5 * self.player_size / (2 * math.cos(math.atan(1 / 3)))))
                    self.player_pieces.append(deadPlayer(self.player.x, self.player.y, 5 * self.player_size / (2 * math.cos(math.atan(1 / 3)))))
                    self.player_pieces.append(deadPlayer(self.player.x, self.player.y, self.player_size))

                    # Kill player
                    self.player_state = 1
                    self.player_dying_delay = 30
                    self.player_invi_dur = 120
                    self.player.killPlayer()

                    if self.live != 0:
                        self.live -= 1
                    else:
                        self.gameState = 1

                    # Split asteroid
                    if a.t == "Large":
                        self.asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        self.asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        self.score += 20
                        self.reward += 20
                    elif a.t == "Normal":
                        self.asteroids.append(Asteroid(a.x, a.y, "Small"))
                        self.asteroids.append(Asteroid(a.x, a.y, "Small"))
                        self.score += 50
                        self.reward += 50

                    else:
                        self.score += 100
                        self.reward += 100

                    self.asteroids.remove(a)

        # Update ship fragments
        for f in self.player_pieces:
            f.updateDeadPlayer(self.disable_display, self.gameDisplay, self.white)
            if f.x > self.display_width or f.x < 0 or f.y > self.display_height or f.y < 0:
                self.player_pieces.remove(f)

        # Check for end of stage
        if len(self.asteroids) == 0 and self.saucer.state == "Dead":
            if self.next_level_delay < 30:
                self.next_level_delay += 1
            else:
                self.stage += 1
                self.intensity = 0
                # Spawn asteroid away of center
                for i in range(self.stage):
                    xTo = self.display_width / 2
                    yTo = self.display_height / 2
                    while xTo - self.display_width / 2 < self.display_width / 4 and yTo - self.display_height / 2 < self.display_height / 4:
                        xTo = random.randrange(0, self.display_width)
                        yTo = random.randrange(0, self.display_height)
                    self.asteroids.append(Asteroid(xTo, yTo, "Large"))
                self.next_level_delay = 0

        # Update intensity
        if self.intensity < self.stage * 450:
            self.intensity += 1

        # Saucer
        if self.saucer.state == "Dead":
            if random.randint(0, 6000) <= (self.intensity * 2) / (self.stage * 9) and self.next_level_delay == 0:
                self.saucer.createSaucer()
                # Only small saucers >40000
                if self.score >= 40000:
                    self.saucer.type = "Small"
        else:
            # Set saucer targer dir
            acc = self.small_saucer_accuracy * 4 / self.stage
            self.saucer.bdir = math.degrees(math.atan2(-self.saucer.y + self.player.y, -self.saucer.x + self.player.x) + math.radians(random.uniform(acc, -acc)))

            self.saucer.updateSaucer()
            self.saucer.drawSaucer(self.gameDisplay, self.white)

            # Check for collision w/ asteroid
            for a in self.asteroids:
                if self.isColliding(self.saucer.x, self.saucer.y, a.x, a.y, a.size + self.saucer.size):
                    # Set saucer state
                    self.saucer.state = "Dead"

                    # Split asteroid
                    if a.t == "Large":
                        self.asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        self.asteroids.append(Asteroid(a.x, a.y, "Normal"))

                    elif a.t == "Normal":
                        self.asteroids.append(Asteroid(a.x, a.y, "Small"))
                        self.asteroids.append(Asteroid(a.x, a.y, "Small"))

                    self.asteroids.remove(a)

            # Check for collision w/ bullet
            for b in self.bullets:
                if self.isColliding(b.x, b.y, self.saucer.x, self.saucer.y, self.saucer.size):
                    # Add points
                    if self.saucer.type == "Large":
                        self.score += 200
                        self.reward += 200
                    else:
                        self.score += 1000
                        self.reward += 1000

                    # Set saucer state
                    self.saucer.state = "Dead"

                    # Remove bullet
                    self.bullets.remove(b)

            # Check collision w/ player
            if self.isColliding(self.saucer.x, self.saucer.y, self.player.x, self.player.y, self.saucer.size):
                if self.player_state != 1:
                    # Create ship fragments
                    self.player_pieces.append(deadPlayer(self.player.x, self.player.y, 5 * self.player_size / (2 * math.cos(math.atan(1 / 3)))))
                    self.player_pieces.append(deadPlayer(self.player.x, self.player.y, 5 * self.player_size / (2 * math.cos(math.atan(1 / 3)))))
                    self.player_pieces.append(deadPlayer(self.player.x, self.player.y, self.player_size))

                    # Kill player
                    self.player_state = 1
                    self.player_dying_delay = 30
                    self.player_invi_dur = 120
                    self.player.killPlayer()
                    self.reward -= 1000

                    if self.live != 0:
                        self.live -= 1
                    else:
                        self.gameState = 1

            # Saucer's bullets
            for b in self.saucer.bullets:
                # Update bullets
                b.updateBullet(self.disable_display, self.gameDisplay, self.white)

                # Check for collision w/ asteroids
                for a in self.asteroids:
                    if self.isColliding(b.x, b.y, a.x, a.y, a.size):
                        # Split asteroid
                        if a.t == "Large":
                            self.asteroids.append(Asteroid(a.x, a.y, "Normal"))
                            self.asteroids.append(Asteroid(a.x, a.y, "Normal"))

                        elif a.t == "Normal":
                            self.asteroids.append(Asteroid(a.x, a.y, "Small"))
                            self.asteroids.append(Asteroid(a.x, a.y, "Small"))

                        # Remove asteroid and bullet
                        self.asteroids.remove(a)
                        self.saucer.bullets.remove(b)

                        break

                # Check for collision w/ player
                if self.isColliding(self.player.x, self.player.y, b.x, b.y, 5):
                    if self.player_state != 1:
                        # Create ship fragments
                        self.player_pieces.append(deadPlayer(self.player.x, self.player.y, 5 * self.player_size / (2 * math.cos(math.atan(1 / 3)))))
                        self.player_pieces.append(deadPlayer(self.player.x, self.player.y, 5 * self.player_size / (2 * math.cos(math.atan(1 / 3)))))
                        self.player_pieces.append(deadPlayer(self.player.x, self.player.y, self.player_size))

                        # Kill player
                        self.player_state = 1
                        self.player_dying_delay = 30
                        self.player_invi_dur = 120
                        self.player.killPlayer()
                        self.reward -= 1000

                        if self.live != 0:
                            self.live -= 1
                        else:
                            self.gameState = 1

                        # Remove bullet
                        if b in self.saucer.bullets:
                            self.saucer.bullets.remove(b)

                if b.life <= 0:
                    try:
                        self.saucer.bullets.remove(b)
                    except ValueError:
                        continue

        # Bullets
        for b in self.bullets:
            # Update bullets
            b.updateBullet(self.disable_display,self.gameDisplay,self.white)

            # Check for bullets collide w/ asteroid
            for a in self.asteroids:
                if b.x > a.x - a.size and b.x < a.x + a.size and b.y > a.y - a.size and b.y < a.y + a.size:
                    # Split asteroid
                    if a.t == "Large":
                        self.asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        self.asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        self.score += 20
                        self.reward += 20

                    elif a.t == "Normal":
                        self.asteroids.append(Asteroid(a.x, a.y, "Small"))
                        self.asteroids.append(Asteroid(a.x, a.y, "Small"))
                        self.score += 50
                        self.reward += 50

                    else:
                        self.score += 100
                        self.reward += 100

                    self.asteroids.remove(a)
                    self.bullets.remove(b)

                    break

            # Destroying bullets
            if b.life <= 0:
                try:
                    self.bullets.remove(b)
                except ValueError:
                    continue

        # Extra live
        if self.score > self.oneUp_multiplier * 10000:
            self.oneUp_multiplier += 1
            #live += 1
            self.playOneUpSFX = 60
        # Play sfx
        if self.playOneUpSFX > 0:
            self.playOneUpSFX -= 1

        # Draw player
        if self.gameState != 1:
            if self.player_state == 1:
                if self.hyperspace == 0:
                    if self.player_dying_delay == 0:
                        if self.player_blink < 5:
                            if self.player_blink == 0:
                                self.player_blink = 10
                            else:
                                self.player.drawPlayer()
                        self.player_blink -= 1
                    else:
                        self.player_dying_delay -= 1
            else:
                self.player.drawPlayer(self.disable_display,self.gameDisplay,self.white)
        else:

            self.live = -1

        # Draw score
        self.drawText(str(self.score), self.white, 60, 20, 40, False)

        # Draw Lives
        # for l in range(self.live + 1):
        #     Player(75 + l * 25, 75).drawPlayer()

        # Update screen
        self.pygameDisplayUpdate()

        # Tick fps
        self.timer.tick(self.fps)
        
        if self.gameState == 0:
            gameOver = False
        else:
            gameOver = True

        return self.reward, gameOver, self.score

    def get_state(self):
        nearest_asteroids_number=8
        asteroids_dist=[[math.sqrt((asteroid.x-self.player.x)**2+(asteroid.y-self.player.y)**2),asteroid ]for asteroid in self.asteroids]
        asteroids_dist.sort(key=lambda asteroid: asteroid[0])
        nearest_asteroids=[asteroid[1] for asteroid in asteroids_dist[0:nearest_asteroids_number]]
        state=[0 for i in range(nearest_asteroids_number*5)]
        for i in range(0,len(nearest_asteroids)*5,5):
            state[i+0]=nearest_asteroids[i//5].x
            state[i+1]=nearest_asteroids[i//5].y
            state[i+2]=nearest_asteroids[i//5].size
            state[i+3]=nearest_asteroids[i//5].dir
            state[i+4]=nearest_asteroids[i//5].speed
        state+=[self.player.x,self.player.y,self.player.dir]
        if self.saucer!=None and self.saucer.state!="Dead":
            state+=[self.saucer.x,self.saucer.y,self.saucer.dir]
            if len(self.saucer.bullets) != 0:
                state+=[self.saucer.bullets[0].x,self.saucer.bullets[0].y,self.saucer.bullets[0].dir]
            else:
                state+=[self.saucer.x,self.saucer.y,self.saucer.dir]
        else:
            state+=[0,0,0,0,0,0]
        return state


