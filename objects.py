import pygame,os
from pygame.math import Vector2
from math import sin,cos,pi,degrees,radians,sqrt
from random import randint

#Sprites
playerImg = pygame.image.load(os.path.join('Sprites', 'ship_player.png'))
gruntImg = pygame.image.load(os.path.join('Sprites', 'ship_grunt.png'))
grunt2Img = pygame.image.load(os.path.join('Sprites', 'ship_grunt2.png'))
flankerImg = pygame.image.load(os.path.join('Sprites', 'ship_flanker.png'))
flanker2Img = pygame.image.load(os.path.join('Sprites', 'ship_flanker2.png'))

playershotImg = pygame.image.load(os.path.join('Sprites', 'shot_player.png'))
enemyshotImg = pygame.image.load(os.path.join('Sprites', 'shot_enemy.png'))


#Groups
player_group = pygame.sprite.Group()
player_shots = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
enemy_shots = pygame.sprite.Group()

all_groups = [player_group, player_shots, enemy_group, enemy_shots]

dtmod = 16 #Rate of updates, since 1000(miliseconds)/60(frames) is 16.




class shot(pygame.sprite.Sprite):
    def __init__(self,x,y,angle,team):
        global player_shots,enemy_shots
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.dmg = 5
        self.spd = 7
        self.angle = angle
        self.spdx = self.spd * cos(angle)
        self.spdy = self.spd * sin(angle)
        self.team = team
        self.life = 300 #Duration, in frames, the shot will exist
        if team == "Green":
            self.image2 = playershotImg
            player_shots.add(self)
        else:
            self.image2 = enemyshotImg
            enemy_shots.add(self)
        self.image = pygame.transform.rotate(self.image2,degrees(angle))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        

    def __str__(self):
        return str((str(self.rect.x),str(self.rect.y)))
    
    def update(self,reference):
        self.x += self.spdx
        self.rect.x = self.x
        self.y += self.spdy
        self.rect.y = self.y

        self.life -= 1
        if self.life < 0: self.kill()


class ship(pygame.sprite.Sprite): #sets up the ship class, which is the base class that represents all space-ships in the game.
    def __init__(self,x,y,team,angle = 0):
    	pygame.sprite.Sprite.__init__(self)
    	self.x = x
    	self.y = y
    	self.angle = angle
        self.team = team     

        self.spdx = 0 #current speed on given axis
        self.spdy = 0
        self.accel = 0 #rate of acceleration
        self.accelx = 0 #current frame's acceleration change on given axis
        self.accely = 0
        self.maxspd = 3.0 #total max speed

        self.maxdelay = 0 #max delay between shots
        self.delay = 0 #shots delay
        self.turnspeed = 0

        self.target = None
        self.aimed = False #Boolean to track whether the ship has finished rotating torwards the current target

    def __str__(self):
        aux = "Ship object at %d x and %d y" % (self.rect.x, self.rect.y)
        return aux

    def update(self,target = None):
        if self.hp <= 0: 
            self.kill()
            return
        if (self.accelx != 0 or self.accely != 0): self.calculateSpeed()
        if target is None: self.rotate(self.target)
        else: self.rotate(target)

        self.x += self.spdx #* dt 
        self.y += self.spdy #* dt

    	self.rect.y = self.y
        self.rect.x = self.x

        self.accelx = 0
        self.accely = 0
        self.delay -= 1
        self.angle = self.angle % (pi*2)
    	if self.spdx != 0 or self.spdy != 0: #Natural deacceleration
    		vector = Vector2(self.spdx,self.spdy)#Derives a vector from the current velocity on both axis and deaccelerates with an opposite vector.
    		angle = vector.as_polar()[1]
    		self.spdx -= (0.5/10.0) * cos(radians(angle)) 
    		self.spdy -= (0.5/10.0) * sin(radians(angle))
    		if cos(radians(angle)) > 0 and self.spdx < 0:
    			self.spdx = 0
    		elif cos(radians(angle)) < 0 and self.spdx > 0:
    			self.spdx = 0
    		if sin(radians(angle)) > 0 and self.spdy < 0:
    			self.spdy = 0
    		elif sin(radians(angle)) < 0 and self.spdy > 0:
    			self.spdy = 0

    def rotate(self,target):
        """Rotates torwards the target, be it a ship or position"""
        self.aimed = False
        if isinstance(target,ship):#Checks whether an ship target has been passed
            vector = Vector2(self.rect.centerx-target.rect.centerx,self.rect.centery-target.rect.centery)
        elif isinstance(target, tuple):        #or an specific position
            vector = Vector2(self.rect.centerx-target[0],self.rect.centery-target[1])
        else: return
        angle = vector.as_polar()[1]
        if (-(angle-180) - degrees(self.angle)) > -4 and (-(angle-180) - degrees(self.angle)) < 4: 
            self.aimed = True #Simple test to check whether the object is already rotated torwards his target
            return
        if -(angle-180) - degrees(self.angle) > 180: #In case the angle overflows from the first quadrant to the fourth
            self.angle -= self.turnspeed#Rotate Right
        elif degrees(self.angle) - -(angle-180) > 180: #In case the angle overflows from the fourth quadrant to the first
            self.angle += self.turnspeed#Rotate left
        else: 
            if -(angle-180) - degrees(self.angle) > degrees(self.angle) - -(angle-180):
                self.angle += self.turnspeed
            else:
                self.angle -= self.turnspeed
    

    def calculateSpeed(self):
        """Calculates the maximum speed of a given object"""
        accel_vector = Vector2(self.accelx,self.accely)
        accel_angle = accel_vector.as_polar()[1]

        self.spdx += self.accelx
        self.spdy -= self.accely #this is inverted because the Y axis is upside-down
        if abs(self.spdx) > abs(self.maxspd * cos(radians(accel_angle))):
            self.spdx = self.maxspd * cos(radians(accel_angle))

        if abs(self.spdy) > abs(self.maxspd * sin(radians(accel_angle))): #these values are also inverted because the Y axis is also inverted
            self.spdy = -(self.maxspd * sin(radians(accel_angle)))
            

    def moveleft(self):
    	self.accelx += self.accel * cos(self.angle+pi/2)
    	self.accely += self.accel * sin(self.angle+pi/2)
   
    def moveright(self):
    	self.accelx += self.accel * cos(self.angle-pi/2)
        self.accely += self.accel * sin(self.angle-pi/2)

    def moveforward(self):
    	self.accelx += self.accel * cos(self.angle)
    	self.accely += self.accel * sin(self.angle)
        
    def moveback(self):
    	self.accelx += self.accel * cos(self.angle-pi)
    	self.accely += self.accel * sin(self.angle-pi)
    	
    def shoot(self):
        if self.delay <= 0:
            self.delay = self.maxdelay
            newshot = shot(self.rect.centerx + ((self.rect.width/1.8) * cos(-self.angle)),#x position
                           self.rect.centery + ((self.rect.height/1.8) * sin(-self.angle)), #y position
                            -(self.angle)+radians(randint(-5,5)), self.team) #angle and team

    def getTarget(self):
        closest = 100000
        if self.team == "Red":
            if len(player_group) > 0:
                for ship in player_group:
                    if sqrt((abs(ship.rect.centerx - self.rect.centerx)**2) + (abs(ship.rect.centery - self.rect.centery)**2)) < closest:
                       closest = sqrt((abs(ship.rect.centerx - self.rect.centerx)**2) + (abs(ship.rect.centery - self.rect.centery)**2))
                       self.target = ship
            else: self.target = None
        else:
            if len(enemy_group) > 0:
                for ship in enemy_group:
                    if sqrt((abs(ship.rect.centerx - self.rect.centerx)**2) + (abs(ship.rect.centery - self.rect.centery)**2)) < closest:
                        closest = sqrt((abs(ship.rect.centerx - self.rect.centerx)**2) + (abs(ship.rect.centery - self.rect.centery)**2))
                        self.target = ship
            else: self.target = None


class player(ship):
    def __init__(self,x,y,team,angle = 0):
        ship.__init__(self,x,y,team,angle)

        self.hp = 100
        self.accel = 0.4
        self.maxspd = 3.0
        self.maxdelay = 5
        self.turnspeed = pi/50

        player_group.add(self)
        self.image2 = pygame.transform.scale(playerImg,(20,20))
        self.image = self.image2
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def rotateleft(self,intensity): #Methods used for rotating the player manually
        self.angle += self.turnspeed * (intensity/-214.0) #As he places the mouse further to the left, mousex gets progressively smaller, hence negative operation

    def rotateright(self,intensity):
        self.angle -= self.turnspeed * (intensity/212.0)#Intensity controls how fast the player rotates, depending on how far he places the mouse on a given side


class grunt(ship):
    def __init__(self,x,y,team,angle = 0):
        ship.__init__(self,x,y,team,angle)
        
        

        self.hp = 20
        self.accel = 0.2
        self.maxspd = 2.0
        self.maxdelay = 20
        self.turnspeed = pi/70

        self.target = None
        self.state = "hunting"

        self.dodgeCount = randint(1,3)
        self.maxDodgeTimer = 120
        self.dodgeTimer = self.maxDodgeTimer

        if self.team == "Green":
            player_group.add(self)
            self.image2 = pygame.transform.scale(grunt2Img,(20,20))
        else:
            enemy_group.add(self)
            self.image2 = pygame.transform.scale(gruntImg,(20,20))

        self.image = self.image2
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


    def ai(self):
        if self.target is None:
            self.getTarget()
        else:
            if self.state == "hunting":
                if (abs(self.target.rect.centerx - self.rect.centerx) < 100) and (abs(self.target.rect.centery - self.rect.centery) < 100):
                    self.shoot()
                    self.moveback()
                elif (abs(self.target.rect.centerx - self.rect.centerx) > 200) and (abs(self.target.rect.centery - self.rect.centery) > 200):
                    self.moveforward()
                else:
                    if self.dodgeTimer > 0 and self.dodgeCount % 2 == 0:
                        self.moveleft()
                        self.shoot()
                        self.dodgeTimer -= 1
                    elif self.dodgeTimer > 0 and self.dodgeCount % 2 != 0:
                        self.moveright()
                        self.shoot()
                        self.dodgeTimer -= 1
                    else:
                        self.getTarget()
                        self.dodgeTimer = self.maxDodgeTimer
                        self.dodgeCount -= 1
                        if self.dodgeCount <= 0:
                            self.dodgeCount = randint(1,3)
                            self.state = "retreating"
            if self.state == "retreating":
                if (abs(self.target.rect.centerx - self.rect.centerx) < 200) and (abs(self.target.rect.centery - self.rect.centery) < 200):
                    self.moveback()
                else:
                    self.state = "hunting"


class flanker(ship):
    def __init__(self,x,y,team,angle = 0):
        ship.__init__(self,x,y,team,angle)

        self.hp = 40
        self.accel = 0.5
        self.maxspd = 4.0
        self.maxdelay = 7
        self.turnspeed = pi/30

        self.target = None
        self.state = "moving"

        self.shootTimer = randint(30,60)

        if self.team == "Green":
            player_group.add(self)
            self.image2 = pygame.transform.scale(flanker2Img,(20,20))
        else:
            enemy_group.add(self)
            self.image2 = pygame.transform.scale(flankerImg,(20,20))
        self.image = self.image2
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


    def getVicinity(self):
        self.xScale = randint(-1,1)
        while self.xScale == 0:
            self.xScale = randint(-1,1)
        self.yScale = randint(-1,1)
        while self.yScale == 0:
            self.yScale = randint(-1,1)
        self.target = (self.target.rect.centerx + (self.xScale*150), self.target.rect.centery + (self.yScale*-150))
        #If the target position is outside of the screens boundaries, re-random it.

    def ai(self):
        if self.target is None:
            self.getTarget()
            if self.target is not None:
                self.getVicinity()
        else:
            if self.state == "moving":
                if abs(self.rect.centerx - self.target[0]) > 100 and abs(self.rect.centery - self.target[1]) > 100:
                    self.moveforward()
                else:
                    self.state = "shooting"
                    self.getTarget()

            if self.state == "shooting":
                if self.shootTimer >= 0:
                    if self.aimed:
                        if self.xScale == -1 and self.yScale == -1:
                            self.moveleft()
                            self.shoot()
                        elif self.xScale == 1 and self.yScale == -1:
                            self.moveright()
                            self.shoot()
                        elif self.xScale == -1 and self.yScale == 1:
                            self.moveleft()
                            self.shoot()
                        elif self.xScale == 1 and self.yScale == 1:
                            self.moveright()
                            self.shoot()
                        self.shootTimer -= 1
                else:
                    self.state = "moving"
                    self.getVicinity()
                    self.shootTimer = randint(30,60)
                

            


