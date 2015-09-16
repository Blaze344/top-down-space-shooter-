import pygame, sys
from pygame.locals import *
from random import randint
from math import sin,cos,pi,degrees,radians,sqrt

import objects,render

pygame.init()

# set up the display
FPS = 60
fpsClock = pygame.time.Clock()
graphwidth = 640
graphheight = 640
DISPLAYSURF = pygame.display.set_mode((graphwidth, graphheight))

bg = pygame.image.load('BG.jpg')	



		

def update():
	for ship in objects.player_group:
		try:
			ship.ai()
			ship.update()
		except AttributeError:
			ship.update()
	for ship in objects.enemy_group:
		#ship.ai()
		ship.update()
	for bullet in objects.player_shots:
		bullet.update(player_ship)
		checkCollision(bullet)
	for bullet in objects.enemy_shots:
		bullet.update(player_ship)
		checkCollision(bullet)
	camera.update()
	camera.draw()
	fpsClock.tick(FPS)
	pygame.display.update()

def checkCollision(shot):
	if shot.team == "Green":
		for ship in objects.enemy_group:
			if shot.rect.centerx in range(ship.rect.x, ship.rect.x+ship.rect.width+1) and \
			   shot.rect.centery in range(ship.rect.y, ship.rect.y+ship.rect.height+1):
			   ship.hp -= shot.dmg
			   shot.kill()
	else:
		for ship in objects.player_group:
			if shot.rect.centerx in range(ship.rect.x, ship.rect.x+ship.rect.width+1) and \
			   shot.rect.centery in range(ship.rect.y, ship.rect.y+ship.rect.height+1):
			   ship.hp -= shot.dmg
			   shot.kill()

forward = False
back = False
left = False
right = False
mouseClicked = False

player_ship = objects.player(320,320,"Green")
#grunt_friend = objects.grunt(150,150,"Green")
#flanker_friend = objects.flanker(200,200,"Green")
flanker_ship = objects.flanker(300,300,"Red")
#grunt_ship = objects.grunt(500,500,"Red")
#grunt_ship = objects.grunt(400,400,"Red")

camera = render.Camera(player_ship,DISPLAYSURF)
prevtime = 0
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


	if forward == True: player_ship.moveforward()
	if back == True: flanker_ship.shoot()
	if left == True: player_ship.moveleft()
	if right == True: player_ship.moveright()
	if mouseClicked == True: player_ship.shoot()
	if mousex < 214: player_ship.rotateleft(mousex-214)
	elif mousex > 428: player_ship.rotateright(mousex-428)


	update() #updates every object and screen every frame

	