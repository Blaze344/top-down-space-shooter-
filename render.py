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
					angleOffset = self.calculateAngleOffset(thing)
					newpos[0] -= thing.rect.width/2*abs(cos(-angleOffset))
					newpos[1] -= thing.rect.height/2*abs(sin(angleOffset))
					image = rot_center(thing.image2,degrees(-angleOffset))
					self.surface.blit(image,(newpos[0],newpos[1]))

	def calculatePosOffset(self,sprite):
		#if not isinstance(sprite,shot):
		vector = Vector2(sprite.rect.x - self.parent.rect.x, sprite.rect.y - self.parent.rect.y)
		#else:
		#vector = Vector2(sprite.rect.centerx - self.parent.rect.centerx, sprite.rect.centery - self.parent.rect.centery)
		distance = vector.as_polar()[0] #sqrt(((sprite.rect.centerx - self.parent.rect.centerx)**2) + ((sprite.rect.centerx - self.parent.rect.centerx)**2))
		angle = vector.as_polar()[1]
		if distance > 650: return None
		newpos = [distance*cos(radians(angle)+self.offset)+320,distance*sin(radians(angle)+self.offset)+480]
		return newpos

	def calculateAngleOffset(self,sprite):
		offset = self.offset - sprite.angle #We subtract here because sprite.angle is already negative
		return offset


	def update(self):
		self.offset = self.parent.angle-pi/2
		self.cameraPos = (self.parent.rect.centerx-320, self.parent.rect.centery-480)






