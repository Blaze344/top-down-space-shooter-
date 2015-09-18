import pygame
from pygame.math import Vector2
from math import sin,cos,pi,degrees,radians,sqrt

from objects import all_groups,shot

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

class Camera(object):
	def __init__(self,parent,surface):
		self.parent = parent
		self.surface = surface

		self.offset = parent.angle
		self.cameraPos = (parent.rect.centerx-320,parent.rect.centery-480)

	def draw(self):
		self.surface.fill((0,0,0))
		for group in all_groups:
			for thing in group:
				newpos = self.calculatePosOffset(thing)
				if newpos is not None: #If the distance from the objects is not greater than the screen
					rotationOffset = self.calculateAngleOffset(thing)
					image = rot_center(thing.image2,degrees(-rotationOffset))
					self.surface.blit(image,(newpos[0],newpos[1]))

	def calculatePosOffset(self,sprite):
		"""Calculates the position the sprite is shown on the screen when taking the parent's rotation and position into account"""
		vector = Vector2(sprite.rect.centerx - self.parent.rect.centerx, sprite.rect.centery - self.parent.rect.centery)#
		distance = vector.as_polar()[0]#Creates a vector between the center position of the parent and the target sprite
		angle = vector.as_polar()[1] #Then converts it to polar coordinates, so it's possible to transform the position based on the angle
		if distance > 650: return None
		newpos = [distance*cos(radians(angle)+self.offset)+320, distance*sin(radians(angle)+self.offset)+480]

		vector = Vector2(sprite.rect.x-sprite.rect.centerx, sprite.rect.y-sprite.rect.centery)#Creates a vector between the objects own center and rect position
		standardAngle = vector.as_polar()[0]#This is the standard angle for drawing the object, being the angle between the center and its top-left point
		angleOffset = self.calculateAngleOffset(sprite)
		newpos[0] -= sprite.rect.width/2*abs(cos(standardAngle-angleOffset)) #Then, returns the new draw position based on the displacement of both angles
		newpos[1] -= sprite.rect.height/2*abs(sin(standardAngle+angleOffset)) #the standard angle and the camera's own angle.
		return newpos

	def calculateAngleOffset(self,sprite):
		"""The difference in angles between the camera and the object"""
		offset = self.offset - sprite.angle #We subtract here because sprite.angle is already negative
		return offset


	def update(self):
		self.offset = self.parent.angle-pi/2
		self.cameraPos = (self.parent.rect.centerx-320, self.parent.rect.centery-480)






