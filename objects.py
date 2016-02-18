import pygame,os
from pygame.math import Vector2
from math import sin,cos,pi,degrees,radians,sqrt
from random import randint
import time



#Sprites
playerImg = pygame.image.load(os.path.join('Sprites', 'ship_player.png'))
gruntImg = pygame.image.load(os.path.join('Sprites', 'ship_grunt.png'))
grunt2Img = pygame.image.load(os.path.join('Sprites', 'ship_grunt2.png'))
flankerImg = pygame.image.load(os.path.join('Sprites', 'ship_flanker.png'))
flanker2Img = pygame.image.load(os.path.join('Sprites', 'ship_flanker2.png'))

playershotImg = pygame.image.load(os.path.join('Sprites', 'shot_player.png'))
enemyshotImg = pygame.image.load(os.path.join('Sprites', 'shot_enemy.png'))

explosionImgs = []
for i in range(1,15):
    explosionImgs.append(pygame.image.load(os.path.join('Sprites','explosions', 'explosion'+str(i)+'.png')))

for i in range(0,14):
    explosionImgs[i] = pygame.transform.scale(explosionImgs[i],(20,20))

#Groups
player_group = pygame.sprite.Group()
player_shots = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
enemy_shots = pygame.sprite.Group()

particles = []
explosions = pygame.sprite.Group()

all_groups = [explosions,particles,player_group, player_shots, enemy_group, enemy_shots]

dtmod = 16 #Rate of updates, since 1000(miliseconds)/60(frames) is 16.

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image




    ## To do, implementar hitbox dentro das coisas




class hitbox(object): #It was necessary to create our own hitbox model due to pygame's rectangle not dealing very well with rotation
    def __init__(self, parent):
        self.center = parent.rect.center
        width = parent.rect.width
        height = parent.rect.height
        self.vertices = [[center[0]-width/2,center[1]-height/2],
                        [center[0]-width/2,center[1]+height/2],
                        [center[0]+width/2,center[1]+height/2],
                        [center[0]+width/2,center[1]-height/2]] #standard position for the rectangle
        self.points = [[center[0]-width/2,center[1]-height/2], #rotated positions
                        [center[0]-width/2,center[1]+height/2],
                        [center[0]+width/2,center[1]+height/2],
                        [center[0]+width/2,center[1]-height/2]]
        self.angle = parent.angle


    def rotationDisplacement(self):
        for i in range(0,4):
            vector = Vector2(self.vertices[i][0] - self.center[0], self.vertices[i][1] - self.center[1])
            distance,angle = vector.as_polar()[0], vector.as_polar()[1]

            newpos = [distance*cos(radians(angle)+self.angle)+self.center[0], distance*sin(radians(angle)+self.angle)+self.center[1]]
            self.points[i] = newpos

    def update(self):
        self.center = parent.rect.center
        self.rotationDisplacement()






class particle(object):
    def __init__(self,x,y,color,size,duration):
        self.rect = pygame.Rect(x-size/2, y-size/2, size, size)
        self.color = color
        self.size = size
        self.duration = duration

        particles.append(self)

    def update(self):
        self.duration -= 1
        if self.duration < 0:
            particles.remove(self)

    def draw(self,pos,surface):
        pygame.draw.rect(surface, self.color, (pos[0], pos[1], self.size, self.size))


class explos(pygame.sprite.Sprite): #The class which one calls when its hp is below 0, creating an explosion where it was

    def __init__(self,x,y):#Always sets the first sprite of the explosion automatically
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, 0, 0)
        self.frame = 0
        explosions.add(self)
    def update(self):#Everytime this method is called, it changes the current sprite to the next until its at the last one
        if self.frame >= len(explosionImgs)-1:
            self.kill()#Then it deletes the whole object.
            return
        self.frame += 1

    def draw(self,pos,surface):
        surface.blit(explosionImgs[self.frame],(pos[0],pos[1]))




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
        self.duration = 180 #Duration, in frames, the shot will exist
        if team == "Green":
            self.image = playershotImg
            player_shots.add(self)
        else:
            self.image = enemyshotImg
            enemy_shots.add(self)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        

    def __str__(self):
        return str((str(self.rect.x),str(self.rect.y)))
    
    def update(self):
        self.x += self.spdx
        self.y += self.spdy
        self.rect.x = self.x
        self.rect.y = self.y

        self.duration -= 1
        if self.duration < 0: self.kill()

    def draw(self,pos,surface):
        surface.blit(self.image,(pos[0],pos[1]))



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
        self.speed = 0
        self.maxspd = 3.0 #total max speed

        self.shotmaxdelay = 0 #max delay between shots
        self.shotdelay = 0 #shots delay
        self.turnspeed = 0

        self.target = None 
        self.aimed = False #Boolean to track whether the ship has finished rotating torwards the current target
        if randint(0,1) == 1:
            self.roaming = 1 #number used to track random roaming direction, 1 being right and -1 being left
        else:
            self.roaming = -1

        self.hptimerMAX = 100
        self.hptimer = 0
        

        

    def __str__(self):
        aux = "Ship object at %d x and %d y" % (self.rect.x, self.rect.y)
        return aux



    
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
    
 

    def thrust(self):
        self.accelx += self.accel * cos(self.angle)
        self.accely += self.accel * sin(self.angle)
        current_milli_time = lambda: int(round(time.time() * 1000))
        if current_milli_time() % 3 <= 1 and self.accelx != 0 and self.accely != 0: #creates particles behind the ship to simulate an engine
            particlePos = [self.rect.centerx + randint(-3,3) + ((self.rect.width/1.8) * -cos(-self.angle)), #x position
                           self.rect.centery + randint(-3,3) + ((self.rect.height/1.8) * -sin(-self.angle))] #y position
            fire = particle(particlePos[0],particlePos[1],(255,255,255),2,20)
        

    def shoot(self):
        if self.shotdelay <= 0:
            self.shotdelay = self.shotmaxdelay
            newshot = shot(self.rect.centerx + ((self.rect.width/1.8) * cos(-self.angle)),#x position
                           self.rect.centery + ((self.rect.height/1.8) * sin(-self.angle)), #y position
                            -(self.angle)+radians(randint(-5,5)), self.team) #angle and team

    def takeDamage(self, cause):
        if isinstance(cause,shot): #Implement explosions as cause sometime
            self.hp -= cause.dmg

        self.hptimer = self.hptimerMAX


    def getTarget(self):
        closest = 500        #range of engagement
        self.target = None
        if self.team == "Red":
            if len(player_group) > 0:
                for ship in player_group:
                    distance = sqrt((abs(ship.rect.centerx - self.rect.centerx)**2) + (abs(ship.rect.centery - self.rect.centery)**2))
                    if distance < closest:
                       closest = distance
                       self.target = ship
        else:
            if len(enemy_group) > 0:
                for ship in enemy_group:
                    if sqrt((abs(ship.rect.centerx - self.rect.centerx)**2) + (abs(ship.rect.centery - self.rect.centery)**2)) < closest:
                        closest = sqrt((abs(ship.rect.centerx - self.rect.centerx)**2) + (abs(ship.rect.centery - self.rect.centery)**2))
                        self.target = ship

    def roam(self):
        if self.speed < self.maxspd/3:
            self.thrust()
        random = randint(0,10000)
        if random < 1000:
            self.angle += pi/40 * self.roaming
        elif random > 9900:
            self.roaming = self.roaming * -1

    def update(self):
        if self.hp <= 0: 
            self.kill()
            explos(self.rect.x+self.rect.width,self.rect.y+self.rect.height)
            return
        self.rotate(self.target)
        

        self.speed = sqrt(self.spdx**2 + self.spdy**2) #module of current speed
        if self.speed <= self.maxspd:                #caps at max speed
            self.spdx += self.accelx
            self.spdy -= self.accely 


        self.x += self.spdx #* dt 
        self.y += self.spdy #* dt

        self.rect.x = self.x
        self.rect.y = self.y

        self.accelx = 0
        self.accely = 0
        self.shotdelay -= 1
        self.angle = self.angle % (pi*2)

        self.hptimer -= 1
        
        if self.spdx != 0 or self.spdy != 0: #Natural deacceleration
            vector = Vector2(self.spdx,self.spdy)#Derives a vector from the current velocity on both axis and deaccelerates with an opposite vector.
            angle = vector.as_polar()[1]
            self.spdx -= (0.5/30.0) * cos(radians(angle)) 
            self.spdy -= (0.5/30.0) * sin(radians(angle))
            if cos(radians(angle)) > 0 and self.spdx < 0:
                self.spdx = 0
            elif cos(radians(angle)) < 0 and self.spdx > 0:
                self.spdx = 0
            if sin(radians(angle)) > 0 and self.spdy < 0:
                self.spdy = 0
            elif sin(radians(angle)) < 0 and self.spdy > 0:
                self.spdy = 0
        
    def draw(self,pos,surface):
        rotatedImage = rot_center(self.image,degrees(self.angle))
        surface.blit(rotatedImage,(pos[0],pos[1]))
        if self.hptimer >= 0: #Draws an small hp bar above the target
            barWidth = self.rect.width * (self.hp/self.hpMAX)
            pygame.draw.rect(surface, self.color, (pos[0], pos[1]+self.rect.height+5, barWidth, 3))


class player(ship):
    def __init__(self,x,y,team,angle = 0):
        ship.__init__(self,x,y,team,angle)

        self.hpMAX = 100.0
        self.hp = self.hpMAX
        self.accel = 0.1
        self.maxspd = 3.0
        self.shotmaxdelay = 5
        self.turnspeed = pi/20

        player_group.add(self)
        self.image = pygame.transform.scale(playerImg,(20,20)) #Original image, as to avoid distortion from multiple rotations
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.color = (0,200,0)


class grunt(ship):
    def __init__(self,x,y,team,angle = 0):
        ship.__init__(self,x,y,team,angle)

        self.hpMAX = 20.0
        self.hp = self.hpMAX
        self.accel = 0.2
        self.maxspd = 2.0
        self.shotmaxdelay = 20
        self.turnspeed = pi/40

        self.target = None
        self.state = "hunting"

        self.dodgeCount = randint(1,3)
        self.maxDodgeTimer = 120
        self.dodgeTimer = self.maxDodgeTimer

        if self.team == "Green":
            player_group.add(self)
            self.image = pygame.transform.scale(grunt2Img,(20,20))
            self.color = (0,200,0)
        else:
            enemy_group.add(self)
            self.image = pygame.transform.scale(gruntImg,(20,20))
            self.color = (200,0,0)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


    def ai(self):
        if self.target is None:
            self.getTarget()
            if self.target is None:
                self.roam()
        else:    
            if self.state == "hunting":
                if (abs(self.target.roamect.centerx - self.rect.centerx) < 100) and (abs(self.target.rect.centery - self.rect.centery) < 100):
                    self.shoot()

                elif (abs(self.target.rect.centerx - self.rect.centerx) > 200) and (abs(self.target.rect.centery - self.rect.centery) > 200):
                    self.thrust()
                else:
                    if self.dodgeTimer > 0 and self.dodgeCount % 2 == 0:
                        self.shoot()
                        self.dodgeTimer -= 1
                    elif self.dodgeTimer > 0 and self.dodgeCount % 2 != 0:
                        self.shoot()
                        self.dodgeTimer -= 1
                    else:
                        self.getTarget()
                        self.dodgeTimer = self.maxDodgeTimer
                        self.dodgeCount -= 1
                        if self.dodgeCount <= 0:
                            self.dodgeCount = randint(1,3)
                            self.state = "retreating"
            elif self.state == "retreating":
                if (abs(self.target.rect.centerx - self.rect.centerx) < 200) and (abs(self.target.rect.centery - self.rect.centery) < 200):
                    pass
                else:
                    self.state = "hunting"


class ace(ship):
    def __init__(self,x,y,team,angle = 0):
        ship.__init__(self,x,y,team,angle)

        self.hpMAX = 40.0
        self.hp = self.hpMAX
        self.accel = 0.05
        self.maxspd = 2.5
        self.shotmaxdelay = 7
        self.turnspeed = pi/40

        self.target = None
        self.targetShip = None #Auxiliar variable to track the current target ship along with the target position
        self.state = "moving"

        randomAngle = randint(0,360)
        self.xScale = cos(radians(randomAngle)) #Auxiliar variables used to track from which direction around the target should the ace pursue
        self.yScale = sin(radians(randomAngle))

        self.shootTimer = randint(30,60)

        if self.team == "Green":
            player_group.add(self)
            self.image = pygame.transform.scale(flanker2Img,(20,20))
            self.color = (0,200,0)
        else:
            enemy_group.add(self)
            self.image = pygame.transform.scale(flankerImg,(20,20))
            self.color = (200,0,0)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


    def getVicinity(self): #gives an random point around the target
        self.target = (self.targetShip.rect.centerx + (self.xScale*70), self.targetShip.rect.centery + (self.yScale*70))

    def ai(self):
        if self.target is not None:
            if self.targetShip.hp <= 0:
                self.targetShip = None
                self.target = None
        if self.target is None:
            self.getTarget()
            self.targetShip = self.target
            if self.target is not None:
                self.getVicinity()
                self.state = "moving"
            else:
                self.roam()
        else:
            if self.state == "moving":
                self.getVicinity()
                if sqrt((self.rect.centerx - self.target[0])**2 +(self.rect.centery - self.target[1])**2) > 50:
                    self.thrust()
                else:
                    self.state = "shooting"
                    self.target = self.targetShip
                    randomAngle = randint(0,360)
                    self.xScale = cos(radians(randomAngle))
                    self.yScale = sin(radians(randomAngle))

            elif self.state == "shooting":
                if self.shootTimer >= 0:
                    if self.aimed:
                        if self.shootTimer % 3 <= 1:
                            self.thrust()
                        self.shoot()
                        self.shootTimer -= 1
                else:
                    self.state = "moving"
                    self.getVicinity()
                    self.shootTimer = randint(30,60)
                

            


