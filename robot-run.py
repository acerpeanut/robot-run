#!/usr/bin/python

import Image
import math
import time

PASSAGE = 0
BARRIER = 1
STOP = 0
SLOW = 1
FAST = 2
BACK = 3

''' distance of fuzzy '''
NEAR = 1
MID = 2
MIDFAR = 4
FAR = 8
BUMP = 16

Radius = 15
StepAng = 0.1
Deflaction = math.pi/3

class enviro:
	def __init__(self,pngFile,x=100,y=100,angle=0):
		a = Image.open(pngFile)
		ld = a.load()
		self.size = a.size
		self.closeCount = 0

		(w,h) = self.size

		self.img = Image.new('RGB',self.size,'white')
		ld2 = self.img.load()

		for i in range(w):
			for j in range(h):
				ld2[i,j] = ld[i,j]

		''' initial environment for robot '''
		self.pic = [[BARRIER if ld[i,j][0]<10 else PASSAGE for i in range(w)] \
			for j in range(h)]
		''' special case: because ld[] is [w,h] '''
		# for i in range(self.size[1]):
		# 	for j in range(self.size[0]):
		# 		if(ld[j,i][0] < 10):
		# 			''' black means BARRIER '''
		# 			self.pic[i][j] = BARRIER
		# 			self.closeCount += 1
		# 		else:
		# 			self.pic[i][j] = PASSAGE 

		(self.x,self.y) = (x,y)
		self.angle = angle

		''' left wheel and right wheel is still '''
		self.wheel0 = STOP
		self.wheel1 = STOP
		print 'close points count : %d' % self.closeCount

	
	''' effective distance is smaller than 80 '''
	def front(self):
		for i in range(80):
			for j in range(-Radius,Radius):
				x1 = math.cos(self.angle) * i + self.x
				''' the after translated point '''
				y1 = math.sin(self.angle) * i + j + self.y
				# if x1>0 and y1>0 and self.pic[int(x1)][int(y1)] == BARRIER:
				# 	return i
				if x1<0 or y1<0 or x1>self.size[1] or y1>self.size[0]:
					return i
				elif self.pic[int(x1)][int(y1)] == BARRIER:
					return i
		else:
			return 80
	def left(self):
		for i in range(80):
			for j in range(-Radius,Radius):
				x1 = math.cos(self.angle + Deflaction) * i + self.x
				''' the after translated point '''
				y1 = math.sin(self.angle + Deflaction) * i + j + self.y
				# if x1>0 and y1>0 and self.pic[int(x1)][int(y1)] == BARRIER:
				if x1<0 or y1<0 or x1>self.size[1] or y1>self.size[0]:
					return i
				elif self.pic[int(x1)][int(y1)] == BARRIER:
					return i
		else:
			return 80
	def right(self):
		for i in range(80):
			for j in range(-Radius,Radius):
				x1 = math.cos(self.angle - Deflaction) * i + self.x
				''' the after translated point '''
				y1 = math.sin(self.angle - Deflaction) * i + j + self.y
				# if x1>0 and y1>0 and self.pic[int(x1)][int(y1)] == BARRIER:
				# 	return i
				if x1<0 or y1<0 or x1>self.size[1] or y1>self.size[0]:
					return i
				elif self.pic[int(x1)][int(y1)] == BARRIER:
					return i
		else:
			return 80

	def run(self):
		''' after one step, axis and angel change '''
		if self.wheel0 == SLOW and self.wheel1 == SLOW:
			slowStep = StepAng * Radius
			''' the distance of slow step '''
			self.x += slowStep * math.cos(self.angle)
			self.y += slowStep * math.sin(self.angle)
			pass
		elif self.wheel0 == STOP and self.wheel1 == STOP:
			pass
		elif self.wheel0 == STOP and self.wheel1 == SLOW:
			self.x = self.x - Radius*math.sin(self.angle) + Radius*math.sin(self.angle+StepAng)
			self.y = self.y + Radius*math.cos(self.angle) - Radius*math.cos(self.angle+StepAng)
			self.angle += StepAng
		elif self.wheel0 == SLOW and self.wheel1 == FAST:
			self.x = self.x - 3*Radius*math.sin(self.angle) + 3*Radius*math.sin(self.angle+StepAng)
			self.y = self.y + 3*Radius*math.cos(self.angle) - 3*Radius*math.cos(self.angle+StepAng)
			self.angle += StepAng
		elif self.wheel0 == SLOW and self.wheel1 == STOP:			
			self.x = self.x + Radius*math.sin(self.angle) - Radius*math.sin(self.angle-StepAng)
			self.y = self.y - Radius*math.cos(self.angle) + Radius*math.cos(self.angle-StepAng)
			self.angle -= StepAng
		elif self.wheel0 == FAST and self.wheel1 == SLOW:
			self.x = self.x + 3*Radius*math.sin(self.angle) - 3*Radius*math.sin(self.angle-StepAng)
			self.y = self.y - 3*Radius*math.cos(self.angle) + 3*Radius*math.cos(self.angle-StepAng)
			self.angle -= StepAng
		elif self.wheel0 == SLOW and self.wheel1 == BACK:
			self.angle -= StepAng 
		elif self.wheel0 == BACK and self.wheel1 == SLOW:
			self.angle += StepAng 
		elif self.wheel0 == BACK and self.wheel1 == BACK:
			slowStep = StepAng * Radius
			self.x -= slowStep * math.cos(self.angle)
			self.y -= slowStep * math.sin(self.angle)

	def fuzzy(self):
		stretch = [Radius+15,Radius+30,Radius+50]
		ret = []
		a = [self.left(),self.front(),self.right()]
		for i in range(3):
			if a[i] < Radius:
				ret.append(BUMP)
			elif a[i] < stretch[0]:
				ret.append(NEAR) 
			elif a[i] < stretch[1]:
				ret.append(MID) 
			elif a[i] < stretch[2]:
				ret.append(MIDFAR)
			else:
				ret.append(FAR)
		return ret 

	def strategy(self):
		l = [
			[[FAR,0xffffff,0xffffff],[STOP,SLOW]],
			[[0xffffff,MID|NEAR|BUMP|MIDFAR,0xffffff],[SLOW,STOP]],
			[[MID,0xffffff,0xffffff],[SLOW,SLOW]],
			[[MIDFAR,0xffffff,0xffffff],[SLOW,FAST]],
			[[NEAR,0xffffff,0xffffff],[FAST,SLOW]]
		]
		a = self.fuzzy()
		for i in l:
			for j in range(3):
				if a[j] & i[0][j] == 0:
					break 
			else:
				(self.wheel0,self.wheel1) = i[1]
				break 
		else:
			(self.wheel0,self.wheel1) = (SLOW,SLOW)

	def isOut(self,x1,y1):
		if x1>0 and y1>0 and x1<self.size[0] and y1<self.size[1] and self.pic[int(x1)][int(y1)] != BARRIER:
			return True

	def store(self):
		# global img
		ld = self.img.load()
		for i in range(-(Radius-5),Radius-5):
			for j in range(-(Radius-5),Radius-5):
				ld[int(self.y+i),int(self.x+j)] = (0,100,200)

	def show(self):
		# img = Image.new('RGB',self.size,'white')
		# ld = img.load()
		# count = 0

		# for i in range(self.size[0]):
		# 	for j in range(self.size[1]):
		# 		if self.pic[j][i] == BARRIER:
		# 			ld[i,j] = (0,255,100)
		# 	# 	else:
		# 	# 		count += 1
		# 	# print self.pic[i]
		# ''' the robot marks blue '''
		# for i in range(int(self.x)-Radius,int(self.x)+Radius):
		# 	for j in range(int(self.y)-Radius,int(self.y)+Radius):
		# 		if j>=0 and i>=0 and j<=self.size[0] and i<self.size[0]:
		# 			ld[j,i] = (0,150,255)

		# ''' front scan marks pure red '''
		# for i in range(80):
		# 	for j in range(-Radius,Radius):
		# 		x1 = math.cos(self.angle) * i + self.x
		# 		''' the after translated point '''
		# 		y1 = math.sin(self.angle) * i + j + self.y
		# 		if self.isOut(x1,y1):
		# 			ld[int(y1),int(x1)] = (255,0,0)
		# 		else:
		# 			break

		# ''' left scan marks nearly red '''
		# for i in range(80):
		# 	for j in range(-Radius,Radius):
		# 		x1 = math.cos(self.angle + Deflaction) * i + self.x
		# 		''' the after translated point '''
		# 		y1 = math.sin(self.angle + Deflaction) * i + j + self.y
		# 		if self.isOut(x1,y1):
		# 			ld[int(y1),int(x1)] = (225,0,0)
		# 		else:
		# 			break
		# ''' right scan marks little red '''
		# for i in range(80):
		# 	for j in range(-Radius,Radius):
		# 		x1 = math.cos(self.angle - Deflaction) * i + self.x
		# 		''' the after translated point '''
		# 		y1 = math.sin(self.angle - Deflaction) * i + j + self.y
		# 		if self.isOut(x1,y1):
		# 			ld[int(y1),int(x1)] = (200,0,0)
		# 		else:
		# 			break

		# print 'len: %d' % len(self.pic)
		# global img
		self.img.save('look.jpg',"JPEG")

if __name__ == '__main__':
	a = enviro('1.png',20,1160)
	c = 10
	while True:
		a.strategy()
		# print "left,front,right:  ", a.left(),a.front(),a.right()
		a.run()
		a.store()
		if c % 10 == 0:
			a.show()
			# time.sleep(2)
		c += 1
