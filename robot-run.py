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

htmFile = file("a.html","w")

head='''
<html>
<body onload="drwMG()">
<img id="mg" src="migong3.png" style="display:none" />
<canvas id="a" width="690" height="690">
</canvas>
<script>
var c=document.getElementById("a")
var cxt=c.getContext("2d")
function drwMG(){
var img=document.getElementById("mg")
cxt.drawImage(img,0,0)	
}
cxt.fillStyle="#FF0000"
var count=1
var timeID=0
var ax=new Array(0
'''

AryCount=0
p=''
foot=''')
function dr(){
	cxt.fillRect(ax[count],ax[count+1],10,10)
	count=count+2
	if(count>=ax.length){
		window.clearInterval(timeID)
	}
}
timeID=window.setInterval("dr()",20)
</script>
</body>
</html>
'''
htmFile.write(head)


class enviro:
	def __init__(self,pngFile,x=100,y=100,angle=0):
		a = Image.open(pngFile)
		ld = a.load()
		self.size = a.size
		self.closeCount = 0
		self.finished = 0

		(w,h) = self.size

		self.img = Image.new('RGB',self.size,'white')
		ld2 = self.img.load()

		for i in range(w):
			for j in range(h):
				ld2[i,j] = ld[i,j]

		''' initial environment for robot '''
		self.pic = [[BARRIER if ld[i,j][0]<10 else PASSAGE for i in range(w)] \
			for j in range(h)]

		(self.x,self.y) = (x,y)
		self.angle = angle

		''' left wheel and right wheel is still '''
		self.wheel0 = STOP
		self.wheel1 = STOP
		print 'close points count : %d' % self.closeCount

	
	''' effective distance is smaller than 80 '''

	def front(self):
		for i in range(80):
			x1 = math.cos(self.angle) * i + self.x
			y1 = math.sin(self.angle) * i + self.y
			if x1<0 or y1<0 or x1>=self.size[1] or y1>=self.size[0]:
				self.finished = 1
				return i
			elif self.pic[int(x1)][int(y1)] == BARRIER:
				return i
		else:
			return 80
	def left(self):
		for i in range(80):
			x1 = math.cos(self.angle + Deflaction) * i + self.x
			y1 = math.sin(self.angle + Deflaction) * i + self.y
			if x1<0 or y1<0 or x1>=self.size[1] or y1>=self.size[0]:
				return i
			elif self.pic[int(x1)][int(y1)] == BARRIER:
				return i
		else:
			return 80
	def right(self):
		for i in range(80):
			x1 = math.cos(self.angle - Deflaction) * i + self.x
			y1 = math.sin(self.angle - Deflaction) * i  + self.y
			if x1<0 or y1<0 or x1>=self.size[1] or y1>=self.size[0]:
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
		stretch = [Radius+25,Radius+29,Radius+35]
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
			[[0xffffff,MID|NEAR|BUMP|MIDFAR,0xffffff],[SLOW,BACK]],
			[[MID,0xffffff,0xffffff],[SLOW,SLOW]],
			[[MIDFAR,0xffffff,0xffffff],[SLOW,FAST]],
			[[NEAR|BUMP,0xffffff,0xffffff],[FAST,SLOW]]
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
			print "some thing wrong!!!!!!"
			print a
			(self.wheel0,self.wheel1) = (SLOW,SLOW)

	def isOut(self,x1,y1):
		if x1>0 and y1>0 and x1<self.size[0] and y1<self.size[1] and self.pic[int(x1)][int(y1)] != BARRIER:
			return True

	def store(self):
		# global img
		global p,AryCount,htmFile
		ld = self.img.load()
		for i in range(-(Radius-5),Radius-5):
			for j in range(-(Radius-5),Radius-5):
				ld[int(self.y+i),int(self.x+j)] = (0,100,200)
		# p += "ax[%d]=%d\nay[%d]=%d\n" % (AryCount,int(self.y),AryCount,int(self.x))
		htmFile.write(",%d,%d" % (int(self.y),int(self.x)))
		AryCount += 1

	def show(self):
		self.img.save('look.jpg',"JPEG")

if __name__ == '__main__':
	a = enviro('migong3.png',20,677)
	c = 10
	while True:
		a.strategy()
		# print "left,front,right:  ", a.left(),a.front(),a.right()
		a.run()
		a.store()
		if a.finished:
			a.show()
			break
		#	time.sleep(2)

#htmFile.write(head)
#htmFile.write(p)
htmFile.write(foot)
htmFile.close()
