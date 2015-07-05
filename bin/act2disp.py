# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time
import math
import thread
import threading
#from colour import Color as Colour
from threading import Thread
import os
import commands as sp
import mpeasing
from random import randint

from neopixel import *


# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 64      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)



hub_home=os.environ.get('HUB_HOME', '/opt/monpanel.com/hub/prod')
flog=open(hub_home + '/log/act2disp.log', 'w+', 0)




####

def LOG(str):
	flog.write(str);
	flog.write("\n");
	flog.flush();


class DisplayThread (threading.Thread):
    def __init__(self, threadID, name, strip, pixels):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.strip = strip
        self.pixels = pixels
        self.pixels_prev = [Color(0,0,0) for i in range(16)]

    def run(self):
        LOG("Starting " + self.name)
	#
	while not time2quit:
        	self.loop()
	#
        LOG("Exiting " + self.name)
	thread.exit()

    def loop(self):
	changed = False
#	print "looping.."
	for i in range(16):
		if self.pixels_prev[i] <> self.pixels[i]:
			changed = True
#			print "changed = True"
			break
	if changed: 
		display_lock.acquire()
		for i in range(16):
			strip.setPixelColor(i, self.pixels[i])
#		print "showing.."
		strip.show()
		display_lock.release()
		for i in range(16):
			self.pixels_prev[i] = self.pixels[i]
	time.sleep(100/1000.0)
#

class SpriteThread (threading.Thread):
    def __init__(self, threadID, name, sprite, pixels, delayMove, delayShine):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.sprite = []
	for i in range(16):
		self.sprite.append(sprite[i])
        self.pixels = pixels
        self.delayMove = delayMove
        self.delayShine = delayShine
        self.changed = False
       # self.composeThread = null
        self.brights = [0 for i in range(16)]
	self.spriteLock = threading.Lock()

    def run(self):
        LOG("Starting " + self.name)
	#
	threadMove = threading.Thread(target=self.move, args=(self.delayMove,))
	threadMove.start()
	threadShine = threading.Thread(target=self.shine, args=(self.delayShine,))
	threadShine.start()
	while threadMove.isAlive() or threadShine.isAlive():
		time.sleep(100/1000.0)
		
	#
	self.sprite[:] = []
        LOG("Removing self from sprites " + self.name)
	compose_lock.acquire()
	sprites.remove(self)
	compose_lock.release()
        LOG("Exiting " + self.name)
	thread.exit()

    def move(self, delay_ms):
	for k in range(32):
#		print "moving " + str(k)
		self.spriteLock.acquire()
#		print "Sprite = " + str(self.sprite[0]) + " " + str(self.sprite[1]) + " " + str(self.sprite[2]) + " " + str(self.sprite[3]) + " " + str(self.sprite[4]) + " " + str(self.sprite[5]) + " " + str(self.sprite[6]) + " " + str(self.sprite[7]) + " " + str(self.sprite[8])
		pix15 = self.sprite[15]
		for i in range(15, 0, -1):
			self.sprite [i] = self.sprite[i-1]
		self.sprite[0] = pix15
#		print "Sprite = " + str(self.sprite[0]) + " " + str(self.sprite[1]) + " " + str(self.sprite[2])
		self.changed = True
		self.spriteLock.release()
		#
		time.sleep(delay_ms/1000.0)
	LOG("move done")

    def shine(self, delay_ms):
	for k in range(0, 251, 50):
		self.spriteLock.acquire()
		for i in range(16):
			self.brights[i] = k
		self.changed = True
		self.spriteLock.release()
		time.sleep(delay_ms/1000.0)
	#
	for k in range(251, 0, -10):
		self.spriteLock.acquire()
		for i in range(16):
			self.brights[i] = k
		self.changed = True
		self.spriteLock.release()
		time.sleep(delay_ms/1000.0)
	LOG("shine done")

#
class StillSpriteThread (SpriteThread):
    def __init__(self, threadID, name, sprite, pixels, delayShine, secShine):
        SpriteThread.__init__(self, threadID, name, sprite, pixels, 0, delayShine)
	self.secShine = secShine


    def move(self, delay_ms):
	a=1

    def shine(self, delay_ms):
	for k in range(0, 251, 50):
		self.spriteLock.acquire()
		for i in range(16):
			self.brights[i] = k
		self.changed = True
		self.spriteLock.release()
		time.sleep(delay_ms/1000.0)
	#
	time.sleep(self.secShine)
	#
	for k in range(251, 0, -10):
		self.spriteLock.acquire()
		for i in range(16):
			self.brights[i] = k
		self.changed = True
		self.spriteLock.release()
		time.sleep(delay_ms/1000.0)
	LOG("shine done")


#

class ComposeThread (threading.Thread):
    def __init__(self, threadID, name, pixels):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.pixels = pixels

    def run(self):
        LOG("Starting " + self.name)
	#
	while not time2quit:
        	self.loop()
	#
        LOG("Exiting " + self.name)
	thread.exit()

    def loop(self):
	try:
		display_lock.acquire()
		for i in range(strip.numPixels()):
			pixels[i] = Color(0, 0, 0)
		compose_lock.acquire()
		for k in range(len(sprites)):
			if sprites[k].isAlive():
			#	print "Alive: " + sprites[k].name
				sprites[k].spriteLock.acquire()
				for i in range(strip.numPixels()):
					p1_r = ( pixels[i] >> 16 ) & 0xFF;
					p1_g = ( pixels[i] >>  8 ) & 0xFF;
					p1_b = ( pixels[i]       ) & 0xFF;
					p2_r = ( sprites[k].sprite[i] >> 16 ) & 0xFF;
					p2_g = ( sprites[k].sprite[i] >>  8 ) & 0xFF;
					p2_b = ( sprites[k].sprite[i]       ) & 0xFF;
					p2_r = p2_r * sprites[k].brights[i]/256;
					p2_g = p2_g * sprites[k].brights[i]/256;
					p2_b = p2_b * sprites[k].brights[i]/256;
					if (p1_r > 0 and p2_r > 0):
						p1_r = ( (p1_r + p2_r)/2 ) & 0xFF;
					else:
						p1_r = ( p1_r + p2_r ) & 0xFF;
					if (p1_g > 0 and p2_g > 0):
						p1_g = ( (p1_g + p2_g)/2 ) & 0xFF;
					else:
						p1_g = ( p1_g + p2_g ) & 0xFF;
					if (p1_b > 0 and p2_b > 0):
						p1_b = ( (p1_b + p2_b)/2 ) & 0xFF;
					else:
						p1_b = ( p1_b + p2_b ) & 0xFF;
					pixels[i] = Color(p1_r, p1_g, p1_b)
				sprites[k].changed = False
				sprites[k].spriteLock.release()
	except Exception as e:
		LOG(str(e))
	finally:
		compose_lock.release()
		display_lock.release()
		#
	time.sleep(100/1000.0)



def clearStrip():
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, Color(0, 0, 0))
	strip.show()


# Main program logic follows:
#if __name__ == '__main__':


# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Intialize the library (must be called once before other functions).
strip.begin()
clearStrip()


pixels=[Color(0,0,0) for i in range(16)]

signal1Sprite=[Color(0,0,0) for i in range(16)]
signal1Sprite[0]=Color(0,0,16)
signal1Sprite[1]=Color(0,0,32)
signal1Sprite[2]=Color(0,0,64)

signal2Sprite=[Color(0,0,0) for i in range(16)]
signal2Sprite[0]=Color(0,16,0)
signal2Sprite[1]=Color(0,32,0)
signal2Sprite[2]=Color(0,64,0)

signal3Sprite=[Color(0,0,0) for i in range(16)]
signal3Sprite[0]=Color(64,32,32)
signal3Sprite[1]=Color(64,32,32)
signal3Sprite[2]=Color(64,32,32)

signal4Sprite=[Color(0,0,0) for i in range(16)]
signal4Sprite[3]=Color(32,32,64)
signal4Sprite[4]=Color(32,32,64)
signal4Sprite[5]=Color(32,32,64)

signal5Sprite=[Color(0,0,0) for i in range(16)]
signal5Sprite[6]=Color(32,64,32)
signal5Sprite[7]=Color(32,64,32)
signal5Sprite[8]=Color(32,64,32)

signal6Sprite=[Color(0,0,0) for i in range(16)]
signal6Sprite[5]=Color(100,44,0)

sprites=[]

display_lock = threading.Lock()
compose_lock = threading.Lock()
time2quit = False

try:
	displayThread = DisplayThread(1, "displayThread", strip, pixels)
	displayThread.start()

	composeThread = ComposeThread(2, "composeThread", pixels)
	composeThread.start()

except Exception as e:
	LOG("Error: unable to start thread")
	LOG(str(e))

try:
	time.sleep(100/1000.0)

	while True:
		if os.path.exists(hub_home + "/tmp/pulldata_signal.dat"): 
			status,result = sp.getstatusoutput("cat " + hub_home + "/tmp/pulldata_signal.dat |cut -d ':' -f2 |cut -d '=' -f1")
			os.remove(hub_home + "/tmp/pulldata_signal.dat")
			th = None
			if result == "at": 
				th = SpriteThread(4, "signal2SpriteThread", signal2Sprite, pixels, 100, 50)
			elif result == "sm": 
				th = SpriteThread(3, "signal1SpriteThread", signal1Sprite, pixels, 50, 50)
			if th is not None:
				compose_lock.acquire()
				sprites.append(th)
				compose_lock.release()
				th.start()
			#
		if os.path.exists(hub_home + "/tmp/rttmon_signal.dat"): 
			status,result = sp.getstatusoutput("cat " + hub_home + "/tmp/rttmon_signal.dat |cut -d ':' -f2 |cut -d '=' -f1")
			os.remove(hub_home + "/tmp/rttmon_signal.dat")
			LOG("RTT result=" + str(result))
			rtt = 1
			try:
				rtt = int(result)
			except Exception as e:
				rtt = 1
			LOG("RTT val=" + str(rtt))
			for i in range(16):
				signal6Sprite[i]=Color(0,0,0)
		#	signal6Sprite[randint(0,15)]=Color(100,44,0)
			nrnd = int(math.log(rtt, 5))
			LOG("nrnd=" + str(nrnd))
			if nrnd > 8:
				nrnd = 8
			if nrnd < 1:
				nrnd = 1
			for i in range(nrnd):
				signal6Sprite[randint(0,15)]=Color(100,44,0)
			th = StillSpriteThread(4, "signal6SpriteThread", signal6Sprite, pixels, 5, 0.15)
			compose_lock.acquire()
			sprites.append(th)
			compose_lock.release()
			th.start()
			#
			LOG("len(sprites) = " + str(len(sprites)))
			#
		if os.path.exists(hub_home + "/tmp/pulldata_start.dat"): 
			os.remove(hub_home + "/tmp/pulldata_start.dat")
			th = StillSpriteThread(5, "signal3SpriteThread", signal3Sprite, pixels, 25, 5)
			compose_lock.acquire()
			sprites.append(th)
			compose_lock.release()
			th.start()
			#
		if os.path.exists(hub_home + "/tmp/pushdata_start.dat"): 
			os.remove(hub_home + "/tmp/pushdata_start.dat")
			th = StillSpriteThread(6, "signal4SpriteThread", signal4Sprite, pixels, 25, 5)
			compose_lock.acquire()
			sprites.append(th)
			compose_lock.release()
			th.start()
			#
		if os.path.exists(hub_home + "/tmp/rttmon_start.dat"): 
			os.remove(hub_home + "/tmp/rttmon_start.dat")
			th = StillSpriteThread(7, "signal5SpriteThread", signal5Sprite, pixels, 25, 5)
			compose_lock.acquire()
			sprites.append(th)
			compose_lock.release()
			th.start()
			#
		time.sleep(500/1000.0)

except KeyboardInterrupt:
	LOG("Ok ok, quitting")
finally:
	time2quit = True;
	displayThread.join()
	composeThread.join()
	for i in range(len(sprites)):
		if sprites[i].isAlive():
			sprites[i].join()
	clearStrip()
	time.sleep(100/1000.0)




