import pygame
from pygame.math import Vector2
from math import sin,cos,pi,degrees,radians,sqrt

from objects import all_groups

graphwidth = 1400
graphheight = 900

MAXDISTANCE = sqrt(graphwidth**2 + graphheight**2)

class Camera(object):
	def __init__(self,parent,surface):
		self.parent = parent
		self.surface = surface

		#self.offset = parent.angle
		self.pos = [self.parent.rect.centerx,self.parent.rect.centery]

		self.maxspd = 4
		self.spdx = 0
		self.spdy = 0
		self.accel = self.maxspd/10.0
		self.accelx = 0
		self.accely = 0

	# def draw(self):                                  Old draw with rotation
	# 	self.surface.fill((0,0,0))
	# 	for group in all_groups:
	# 		for thing in group:
	# 			newpos = self.calculatePosOffset(thing)
	# 			if newpos is not None: #If the distance from the objects is not greater than the screen
	# 				angleOffset = self.calculateAngleOffset(thing)
	# 				vector = Vector2(thing.rect.x-thing.rect.centerx, thing.rect.y-thing.rect.centery)#Creates a vector between the objects own center and rect position
	# 				standardAngle = vector.as_polar()[0]#This is the standard angle for drawing the object, being the angle between the center and its top-left point
	# 				newpos[0] -= thing.rect.width/2*abs(cos(standardAngle-angleOffset)) #Then, returns the new draw position based on the displacement of both angles
	# 				newpos[1] -= thing.rect.height/2*abs(sin(standardAngle+angleOffset)) #the standard angle and the camera's own angle.
	# 				image = rot_center(thing.image2,degrees(-angleOffset))
	# 				self.surface.blit(image,(newpos[0],newpos[1]))

	# def calculatePosOffset(self,sprite):
	# 	"""Calculates the position the sprite is shown on the screen when taking the parent's rotation and position into account"""
	# 	vector = Vector2(sprite.rect.centerx - self.pos[0], sprite.rect.centery - self.pos[1])
	# 	distance = vector.as_polar()[0]#Creates a vector between the center position of the parent and the target sprite
	# 	angle = vector.as_polar()[1] #Then converts it to polar coordinates, so it's possible to transform the position based on the angle
	# 	if distance > 400: return None
	# 	newpos = [distance*cos(radians(angle)+self.offset)+320, distance*sin(radians(angle)+self.offset)+480]
	# 	return newpos

	# def calculateAngleOffset(self,sprite):
	# 	"""The difference in angles between the camera and the object"""
	# 	offset = self.offset - sprite.angle #We subtract here because sprite.angle is already negative
	# 	return offset

	def render(self):
		self.surface.fill((0,0,0))
		for group in all_groups:
			for thing in group:
				newpos = self.calculatePosOffset(thing)
				if newpos is not None: #If the distance from the camera to the object is not greater than the screen
					thing.draw(newpos,self.surface)
	 				
		pygame.display.update()

	def calculatePosOffset(self,sprite):
		distance = sqrt((sprite.rect.centerx - self.pos[0])**2 + (sprite.rect.centery - self.pos[1])**2)
		if distance > MAXDISTANCE: return None #MAXDISTANCE is the distance to the screen's borders
		newpos = [sprite.rect.centerx - self.pos[0] + graphwidth/2 - sprite.rect.width/2, sprite.rect.centery - self.pos[1] + graphheight/2 - sprite.rect.height/2]
		return newpos 

	def update(self):
		self.pos[0] = self.parent.rect.centerx
		self.pos[1] = self.parent.rect.centery


		self.accelx = 0
		self.accely = 0
		if self.spdx != 0 or self.spdy != 0: #Natural deacceleration
			vector = Vector2(self.spdx,self.spdy)#Derives a vector from the current velocity on both axis and deaccelerates with an opposite vector.
			angle = radians(vector.as_polar()[1])
			self.spdx -= (0.5/10.0) * cos(angle) 
			self.spdy -= (0.5/10.0) * sin(angle)
			if cos(angle) > 0 and self.spdx < 0:
				self.spdx = 0
			elif cos(angle) < 0 and self.spdx > 0:
				self.spdx = 0
			if sin(angle) > 0 and self.spdy < 0:
				self.spdy = 0
			elif sin(angle) < 0 and self.spdy > 0:
				self.spdy = 0
			if abs(self.spdx) < 1.0:
				self.spdx = 0
			if abs(self.spdy) < 1.0:
				self.sdpy = 0




	def move(self):
		vector = Vector2(self.parent.rect.centerx - self.pos[0], self.parent.rect.centery - self.pos[1])
		angle = radians(vector.as_polar()[1])
		self.accelx += self.accel * cos(angle)
		self.accely += self.accel * sin(-angle)






