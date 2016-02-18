import pygame, sys, time
from pygame.locals import *
from random import randint
from math import sin,cos,pi,degrees,radians,sqrt

from time import sleep
import objects,render

pygame.init()

# set up the display
FPS = 60
fpsClock = pygame.time.Clock()

DISPLAYSURF = pygame.display.set_mode((render.graphwidth, render.graphheight))

bg = pygame.image.load('BG.jpg')	



		

def update():
	for ship in objects.player_group:
		try:
			ship.ai()
			ship.update()
		except AttributeError:
			ship.update()
	for ship in objects.enemy_group:
		ship.ai()
		ship.update()
	for bullet in objects.player_shots:
		bullet.update()
		checkCollision(bullet)
	for bullet in objects.enemy_shots:
		bullet.update()
		checkCollision(bullet)
	for particle in objects.particles:
		particle.update()
	for explosion in objects.explosions:
		explosion.update()
	camera.update()
	camera.render()
	fpsClock.tick(FPS)


#def checkCollision(shot):
#	if shot.team == "Green":
#		for ship in objects.enemy_group:


def checkCollision(shot):
	if shot.team == "Green":
		for ship in objects.enemy_group:
			if (shot.rect.centerx > ship.rect.x and shot.rect.centerx < ship.rect.x + ship.rect.width) and \
			   (shot.rect.centery > ship.rect.y and shot.rect.centery < ship.rect.y + ship.rect.height):
			   ship.takeDamage(shot)
			   shot.kill()
	else:
		for ship in objects.player_group:
			if (shot.rect.centerx > ship.rect.x and shot.rect.centerx < ship.rect.x + ship.rect.width) and \
			   (shot.rect.centery > ship.rect.y and shot.rect.centery < ship.rect.y + ship.rect.height):
			   ship.takeDamage(shot)
			   shot.kill()

forward = False
back = False
left = False
right = False
mouseClicked = False

#player_ship = objects.player(200,200,"Green")
reference = objects.particle(0,0,(155,40,40),50,20000)


#for i in range(5):
#	grunt_friend = objects.grunt(400,60*i,"Green",pi)
#	grunt_enemy = objects.grunt(-400,60*i,"Red")

for i in range(5):
	ace_friend = objects.ace(400,-200 + 70*i,"Green",pi)
	ace_enemy = objects.ace(-400,-200 + 70*i,"Red")
	#ace_friend = objects.ace(-50 + 50*i, -600,"Green",(3*pi)/2)
	#ace_enemy = objects.ace(-50 + 50*i, 600,"Red",pi/2)

camera = render.Camera(reference,DISPLAYSURF)
prevtime = 0
sleep(1)
while True:
	#print camera.calculatePosOffset(player_ship)
	nowtime = pygame.time.get_ticks()
	dt = nowtime-prevtime #delta time
	prevtime = pygame.time.get_ticks()#Will be used later, when the game speed is dictate by time rather than frames
	for event in pygame.event.get(): # event handling loop
	    if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
	        pygame.quit()#Pressing the up and escape keys at the same time will quit the game.
	        sys.exit()
	    elif event.type == KEYDOWN:
	    	if event.key == 119: forward = True
	    	elif event.key == 115: back = True
	    	elif event.key == 97: left = True
	    	elif event.key == 100: right = True

	    elif event.type == KEYUP:
	    	if event.key == 119: forward = False
	    	elif event.key == 115: back = False
	    	elif event.key == 97: left = False
	    	elif event.key == 100: right = False

	    

	    elif event.type == MOUSEMOTION:#Handles the mouse movement
	        mousex, mousey = event.pos
	    elif event.type == MOUSEBUTTONUP:
	        mousex, mousey = event.pos #When the mouse buttom is released, it causes mouseClicked to be False.
	        mouseClicked = False	
	    elif event.type == MOUSEBUTTONDOWN: #While the mouse buttom is pressed, mouse(is)Clicked.
	        mousex, mousey = event.pos
	        mouseClicked = True


	if forward == True: player_ship.thrust()
	if back == True: player_ship.thrust()
	#if left == True: player_ship.moveleft()
	#if right == True: player_ship.moveright()
	if mouseClicked == True: player_ship.shoot()
	relMouse = (camera.pos[0] - render.graphwidth/2 + mousex, camera.pos[1] - render.graphheight/2 + mousey)
	#player_ship.rotate(relMouse)



	update() #updates every object and screen every frame

	