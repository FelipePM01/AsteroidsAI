import pygame
import Asteroids
import random
import math
import numpy as np
import Utils

pygame.init()

snd_fire = pygame.mixer.Sound("Sounds/fire.wav")
snd_bangL = pygame.mixer.Sound("Sounds/bangLarge.wav")
snd_bangM = pygame.mixer.Sound("Sounds/bangMedium.wav")
snd_bangS = pygame.mixer.Sound("Sounds/bangSmall.wav")
snd_extra = pygame.mixer.Sound("Sounds/extra.wav")
snd_saucerB = pygame.mixer.Sound("Sounds/saucerBig.wav")
snd_saucerS = pygame.mixer.Sound("Sounds/saucerSmall.wav")

white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)

player_size = 10
fd_fric = 0.5
bd_fric = 0.1
player_max_speed = 20
player_max_rtspd = 10
bullet_speed = 15
saucer_speed = 5
small_saucer_accuracy = 10
display_width = 800
display_height = 600
display_dims = (display_width,display_height)

def isColliding(x, y, xTo, yTo, size):
    if x > xTo - size and x < xTo + size and y > yTo - size and y < yTo + size:
        return True
    return False

class Game:
    def __init__(self, model_playing, disable_display, fps, model):
        self.MODEL_PLAYING = model_playing
        self.DISABLE_DISPLAY = disable_display
        self.FPS = fps
        self.MODEL = model
        
        self.timer = pygame.time.Clock()

        if not disable_display:
            self.snd_fire = pygame.mixer.Sound("Sounds/fire.wav")
            self.snd_bangL = pygame.mixer.Sound("Sounds/bangLarge.wav")
            self.snd_bangM = pygame.mixer.Sound("Sounds/bangMedium.wav")
            self.snd_bangS = pygame.mixer.Sound("Sounds/bangSmall.wav")
            self.snd_extra = pygame.mixer.Sound("Sounds/extra.wav")
            self.snd_saucerB = pygame.mixer.Sound("Sounds/saucerBig.wav")
            self.snd_saucerS = pygame.mixer.Sound("Sounds/saucerSmall.wav")
            self.gameDisplay = pygame.display.set_mode((display_width, display_height))
            pygame.display.set_caption("Asteroids")

    def playSound(self, *args):
        if self.DISABLE_DISPLAY:
            return
        pygame.mixer.Sound.play(*args)

    def gameDisplayFill(self, color):
        if self.DISABLE_DISPLAY:
            return
        self.gameDisplay.fill(color)

    def pygameDisplayUpdate(self):
        if self.DISABLE_DISPLAY:
            return
        pygame.display.update()

    def drawLine(self, origin, vec):

        if self.DISABLE_DISPLAY:
            return

        steps = np.linspace(0.0,1.0,100)
        vec_x = origin[0]+(vec[0]*steps)
        vec_y = origin[1]+(vec[1]*steps)
        vec_y[vec_y>display_height]-=display_height
        vec_y[vec_y<0]+=display_height
        vec_x[vec_x>display_width]-=display_width
        vec_x[vec_x<0]+=display_width

        points = [i for i in zip(list(vec_x), list(vec_y))]

        for point in points:
            pygame.draw.circle(self.gameDisplay, red, point, 1)
    
    

    # Create function to draw texts
    def drawText(self, msg, color, x, y, s, center=True):
        if self.DISABLE_DISPLAY:
            return
        screen_text = pygame.font.SysFont("Calibri", s).render(msg, True, color)
        if center:
            rect = screen_text.get_rect()
            rect.center = (x, y)
        else:
            rect = (x, y)
        self.gameDisplay.blit(screen_text, rect)

    def gameLoop(self, startingState):
        # Init variables
        gameState = startingState
        player_state = "Alive"
        player_blink = 0
        player_pieces = []
        player_dying_delay = 0
        player_invi_dur = 0
        hyperspace = 0
        next_level_delay = 0
        bullet_capacity = 4
        bullets = []
        asteroids = []
        stage = 3
        score = 0
        live = 0#2
        oneUp_multiplier = 1
        playOneUpSFX = 0
        intensity = 0
        player = Asteroids.Player(display_width / 2, display_height / 2, self)
        saucer = Asteroids.Saucer(self)

        # Main loop
        while gameState != "Exit":
            # Game menu
            if gameState == "Game Over":
                return
            while gameState == "Menu":
                self.gameDisplayFill(black)
                self.drawText("ASTEROIDS", white, display_width / 2, display_height / 2, 100)
                self.drawText("Press any key to START", white, display_width / 2, display_height / 2 + 100, 50)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameState = "Exit"
                    if event.type == pygame.KEYDOWN:
                        gameState = "Playing"
                self.pygameDisplayUpdate()
                self.timer.tick(5)

            # User inputs
            if self.MODEL_PLAYING:
                # manda estado do jogo pro modelo
                asteroidParams = [Utils.getThreatParams(player, a, a.speed,display_dims) for a in asteroids]
                asteroidParams.sort(key=lambda asteroid: asteroid[4], reverse = True)

                if len(asteroidParams) == 1:
                    asteroidParams.append(asteroidParams[0])

                modelParams = [np.inf,0,0,90,np.inf,0,0,90]
                for index, asteroid in enumerate(asteroidParams):
                    if index == 2:
                        break
                    for i in range(4):
                        modelParams[i+index*4] = asteroid[i]

                if saucer != None and saucer.state == "Alive":
                    modelParams += Utils.getThreatParams(player, saucer, saucer_speed, display_dims)
                else:
                    modelParams += [np.inf,0,0,90]

                if saucer != None and len(saucer.bullets) > 0:
                    modelParams += Utils.getThreatParams(player, saucer.bullets[0], bullet_speed, display_dims)
                else:
                    modelParams += [np.inf,0,0,90]
                
                playerSpeed, _ = Utils.recToPolar(player.hspeed, player.vspeed)
                modelParams.append(playerSpeed)

                action = self.model.getAction(modelParams)

                if action[0]==1:
                    player.thrust=True
                else:
                    player.thrust=False

                if action[1] == 1 and action[2] == 0:
                    player.rtspd = player_max_rtspd
                elif action[2]==1 and action[1]==0:
                    player.rtspd= -player_max_rtspd
                else: 
                    player.rtspd=0
                if action[3]==1 and len(bullets) < bullet_capacity:
                    bullets.append(Asteroids.Bullet(player.x, player.y, player.dir, self))

                # Update player
                player.updatePlayer()

                # retorna ação
                pass
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameState = "Exit"
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            player.thrust = True
                        if event.key == pygame.K_LEFT:
                            player.rtspd = -player_max_rtspd
                        if event.key == pygame.K_RIGHT:
                            player.rtspd = player_max_rtspd
                        if event.key == pygame.K_SPACE and player_dying_delay == 0 and len(bullets) < bullet_capacity:
                            bullets.append(Asteroids.Bullet(player.x, player.y, player.dir, self))
                            # Play SFX
                            self.playSound(snd_fire)
                        if gameState == "Game Over":
                            if event.key == pygame.K_r:
                                gameState = "Exit"
                                self.gameLoop("Playing")
                        if event.key == pygame.K_LSHIFT:
                            hyperspace = 30
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_UP:
                            player.thrust = False
                        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                            player.rtspd = 0

            # Update player
            player.updatePlayer()

            # Checking player invincible time
            if player_invi_dur != 0:
                player_invi_dur -= 1
            elif hyperspace == 0:
                player_state = "Alive"

            # Reset display
            self.gameDisplayFill(black)

            # Hyperspace
            if hyperspace != 0:
                player_state = "Died"
                hyperspace -= 1
                if hyperspace == 1:
                    player.x = random.randrange(0, display_width)
                    player.y = random.randrange(0, display_height)

            # Check for collision w/ asteroid
            for a in asteroids:
                vec = Utils.threatDistance(player, a, (display_width,display_height)) 
                self.drawLine((player.x,player.y),vec)
                dist, angleInSight, threatRelSpeed, bearing = Utils.getThreatParams(player, a, a.speed,(display_width,display_height))
                #self.drawText(f'{vec[0]:.2f}, {vec[1]:.2f}, {(Game.angle(vec)-player.dir):.2f} {(a.dir-player.dir):.2f}', white, a.x, a.y-a.size, 20)
                self.drawText(f'{dist:.2f}, {angleInSight:.2f}, {threatRelSpeed:.2f}, {bearing:.2f}', white, a.x, a.y-a.size, 20)
                a.updateAsteroid()
                if player_state != "Died":
                    if isColliding(player.x, player.y, a.x, a.y, a.size):
                        # Create ship fragments
                        player_pieces.append(Asteroids.deadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3))),self))
                        player_pieces.append(Asteroids.deadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3))),self))
                        player_pieces.append(Asteroids.deadPlayer(player.x, player.y, player_size,self))

                        # Kill player
                        player_state = "Died"
                        player_dying_delay = 30
                        player_invi_dur = 120
                        player.killPlayer()

                        if live != 0:
                            live -= 1
                        else:
                            gameState = "Game Over"

                        # Split asteroid
                        if a.t == "Large":
                            asteroids.append(Asteroids.Asteroid(a.x, a.y, "Normal",self))
                            asteroids.append(Asteroids.Asteroid(a.x, a.y, "Normal",self))
                            score += 20
                            # Play SFX
                            self.playSound(snd_bangL)
                        elif a.t == "Normal":
                            asteroids.append(Asteroids.Asteroid(a.x, a.y, "Small",self))
                            asteroids.append(Asteroids.Asteroid(a.x, a.y, "Small",self))
                            score += 50
                            # Play SFX
                            self.playSound(snd_bangM)
                        else:
                            score += 100
                            # Play SFX
                            self.playSound(snd_bangS)
                        asteroids.remove(a)

            # Update ship fragments
            for f in player_pieces:
                f.updateDeadPlayer()
                if f.x > display_width or f.x < 0 or f.y > display_height or f.y < 0:
                    player_pieces.remove(f)

            # Check for end of stage
            if len(asteroids) == 0 and saucer.state == "Dead":
                if next_level_delay < 30:
                    next_level_delay += 1
                else:
                    stage += 1
                    intensity = 0
                    # Spawn asteroid away of center
                    for i in range(stage):
                        xTo = display_width / 2
                        yTo = display_height / 2
                        while xTo - display_width / 2 < display_width / 4 and yTo - display_height / 2 < display_height / 4:
                            xTo = random.randrange(0, display_width)
                            yTo = random.randrange(0, display_height)
                        asteroids.append(Asteroids.Asteroid(xTo, yTo, "Large",self))
                    next_level_delay = 0

            # Update intensity
            if intensity < stage * 450:
                intensity += 1

            # Saucer
            if saucer.state == "Dead":
                if random.randint(0, 6000) <= (intensity * 2) / (stage * 9) and next_level_delay == 0:
                    saucer.createSaucer()
                    # Only small saucers >40000
                    if score >= 40000:
                        saucer.type = "Small"
            else:
                # Set saucer targer dir
                acc = small_saucer_accuracy * 4 / stage
                saucer.bdir = math.degrees(math.atan2(-saucer.y + player.y, -saucer.x + player.x) + math.radians(random.uniform(acc, -acc)))

                saucer.updateSaucer()
                saucer.drawSaucer()

                # Check for collision w/ asteroid
                for a in asteroids:
                    if isColliding(saucer.x, saucer.y, a.x, a.y, a.size + saucer.size):
                        # Set saucer state
                        saucer.state = "Dead"

                        # Split asteroid
                        if a.t == "Large":
                            asteroids.append(Asteroids.Asteroid(a.x, a.y, "Normal",self))
                            asteroids.append(Asteroids.Asteroid(a.x, a.y, "Normal",self))
                            # Play SFX
                            self.playSound(snd_bangL)
                        elif a.t == "Normal":
                            asteroids.append(Asteroids.Asteroid(a.x, a.y, "Small",self))
                            asteroids.append(Asteroids.Asteroid(a.x, a.y, "Small",self))
                            # Play SFX
                            self.playSound(snd_bangM)
                        else:
                            # Play SFX
                            self.playSound(snd_bangS)
                        asteroids.remove(a)

                # Check for collision w/ bullet
                for b in bullets:
                    if isColliding(b.x, b.y, saucer.x, saucer.y, saucer.size):
                        # Add points
                        if saucer.type == "Large":
                            score += 200
                        else:
                            score += 1000

                        # Set saucer state
                        saucer.state = "Dead"

                        # Play SFX
                        self.playSound(snd_bangL)

                        # Remove bullet
                        bullets.remove(b)

                # Check collision w/ player
                if isColliding(saucer.x, saucer.y, player.x, player.y, saucer.size):
                    if player_state != "Died":
                        # Create ship fragments
                        player_pieces.append(Asteroids.deadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3))),self))
                        player_pieces.append(Asteroids.deadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3))),self))
                        player_pieces.append(Asteroids.deadPlayer(player.x, player.y, player_size,self))

                        # Kill player
                        player_state = "Died"
                        player_dying_delay = 30
                        player_invi_dur = 120
                        player.killPlayer()

                        if live != 0:
                            live -= 1
                        else:
                            gameState = "Game Over"

                        # Play SFX
                        self.playSound(snd_bangL)

                # Saucer's bullets
                for b in saucer.bullets:
                    # Update bullets
                    b.updateBullet()
                    vec = Utils.threatDistance(player, b, (display_width,display_height))
                    self.drawLine((player.x,player.y),vec)

                    # Check for collision w/ asteroids
                    for a in asteroids:
                        if isColliding(b.x, b.y, a.x, a.y, a.size):
                            # Split asteroid
                            if a.t == "Large":
                                asteroids.append(Asteroids.Asteroid(a.x, a.y, "Normal",self))
                                asteroids.append(Asteroids.Asteroid(a.x, a.y, "Normal",self))
                                # Play SFX
                                self.playSound(snd_bangL)
                            elif a.t == "Normal":
                                asteroids.append(Asteroids.Asteroid(a.x, a.y, "Small",self))
                                asteroids.append(Asteroids.Asteroid(a.x, a.y, "Small",self))
                                # Play SFX
                                self.playSound(snd_bangL)
                            else:
                                # Play SFX
                                self.playSound(snd_bangL)

                            # Remove asteroid and bullet
                            asteroids.remove(a)
                            saucer.bullets.remove(b)

                            break

                    # Check for collision w/ player
                    if isColliding(player.x, player.y, b.x, b.y, 10):
                        if player_state != "Died":
                            # Create ship fragments
                            player_pieces.append(Asteroids.deadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3))),self))
                            player_pieces.append(Asteroids.deadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3))),self))
                            player_pieces.append(Asteroids.deadPlayer(player.x, player.y, player_size,self))

                            # Kill player
                            player_state = "Died"
                            player_dying_delay = 30
                            player_invi_dur = 120
                            player.killPlayer()

                            if live != 0:
                                live -= 1
                            else:
                                gameState = "Game Over"

                            # Play SFX
                            self.playSound(snd_bangL)

                            # Remove bullet
                            if b in saucer.bullets:
                                saucer.bullets.remove(b)

                    if b.life <= 0:
                        try:
                            saucer.bullets.remove(b)
                        except ValueError:
                            continue

            # Bullets
            for b in bullets:
                # Update bullets
                b.updateBullet()

                # Check for bullets collide w/ asteroid
                for a in asteroids:
                    if b.x > a.x - a.size and b.x < a.x + a.size and b.y > a.y - a.size and b.y < a.y + a.size:
                        # Split asteroid
                        if a.t == "Large":
                            asteroids.append(Asteroids.Asteroid(a.x, a.y, "Normal",self))
                            asteroids.append(Asteroids.Asteroid(a.x, a.y, "Normal",self))
                            score += 20
                            # Play SFX
                            self.playSound(snd_bangL)
                        elif a.t == "Normal":
                            asteroids.append(Asteroids.Asteroid(a.x, a.y, "Small",self))
                            asteroids.append(Asteroids.Asteroid(a.x, a.y, "Small",self))
                            score += 50
                            # Play SFX
                            self.playSound(snd_bangM)
                        else:
                            score += 100
                            # Play SFX
                            self.playSound(snd_bangS)
                        asteroids.remove(a)
                        bullets.remove(b)

                        break

                # Destroying bullets
                if b.life <= 0:
                    try:
                        bullets.remove(b)
                    except ValueError:
                        continue

            # Extra live
            if score > oneUp_multiplier * 10000:
                oneUp_multiplier += 1
                #live += 1
                playOneUpSFX = 60
            # Play sfx
            if playOneUpSFX > 0:
                playOneUpSFX -= 1
                self.playSound(snd_extra, 60)

            # Draw player
            if gameState != "Game Over":
                if player_state == "Died":
                    if hyperspace == 0:
                        if player_dying_delay == 0:
                            if player_blink < 5:
                                if player_blink == 0:
                                    player_blink = 10
                                else:
                                    player.drawPlayer()
                            player_blink -= 1
                        else:
                            player_dying_delay -= 1
                else:
                    player.drawPlayer()
            else:
                self.drawText("Game Over", white, display_width / 2, display_height / 2, 100)
                self.drawText("Press \"R\" to restart!", white, display_width / 2, display_height / 2 + 100, 50)
                live = -1

            # Draw score
            self.drawText(str(score), white, 60, 20, 40, False)

            # Draw Lives
            for l in range(live + 1):
                Asteroids.Player(75 + l * 25, 75,self).drawPlayer()

            # Update screen
            self.pygameDisplayUpdate()

            # Tick fps
            self.timer.tick(self.FPS)
            print(self.timer.get_fps(), gameState)


    # Create funtion to chek for collision
        

mygame = Game(False, False, 30, None)
mygame.gameLoop("Menu")

pygame.quit()