#
#http://blog.oscarliang.net/raspberry-pi-and-arduino-connected-serial-gpio/

import os
import sqlite3 as lite 
import serial
import re
import time
import RPi.GPIO as GPIO 
#import crc16
from monutils import neodisplay

hub_home=os.environ.get('HUB_HOME', '/opt/monpanel.com/hub/prod')

conn = None
conn = lite.connect(hub_home + '/dat/local.db') 
cur = conn.cursor() 

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
ser.open()

flog=open(hub_home + '/log/pulldata.log', 'w+', 0)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

def resetradio():
	GPIO.setup(7, GPIO.OUT)
	GPIO.output(7, GPIO.LOW)
	time.sleep(0.1)
	GPIO.output(7, GPIO.HIGH)
	time.sleep(0.1)

# http://www.lammertbies.nl/comm/info/crc-calculation.html
#
def crc16(buff, crc = 0, poly = 0xa001):
    l = len(buff)
    i = 0
    while i < l:
        ch = ord(buff[i])
        uc = 0
        while uc < 8:
            if (crc & 1) ^ (ch & 1):
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
            ch >>= 1
            uc += 1
        i += 1
    return crc

def LOG(str):
	flog.write(str);
	flog.write("\n");
	flog.flush();

#def neodisplay(name, data):
#	try:
#		f = open(hub_home + '/tmp/' + name + '.dat','w')
#		f.truncate()
#		f.write(data + '\n')
#	except Exception as e:
#		LOG(str(e))
#	finally:
#		f.close()
#


#ser.write("testing")

neodisplay(hub_home, 'pulldata_start', 'dummy')

resetradio()
lt1 = time.time()
try:
        while 1:
		lt2 = time.time()
		# if no data within 5 min, then reset atmega
		if lt2-lt1 > 300:
			resetradio()
			time.sleep(1)
			lt1 = time.time()

                response = ser.readline()
		#response = "DATA#TU12-9K78:t=25:h=27:v=3.3:c=19:10719#\n"
                if not (response == ""):
                        data = response.rstrip('\n')
			LOG(data);
			if (0 != data.find("DATA#")): continue
			data = data[5:-2]
			#data = data[:-1]
			#LOG(data)
			data_wo_crc = data[0:data.rfind(':')]
			#LOG("DATA_WO_CRC = " + data_wo_crc)
			arr = re.split(':',data)
			crc =  arr[len(arr)-1]
			#LOG("CRC16=" + crc)
			#crc_calc = crc16.calcString(data_wo_crc, 0) 
			crc_calc = crc16(data_wo_crc)
			#print "CRC16_CALC=" + str(crc_calc)
			if int(crc) == crc_calc: 
				lt1 = time.time()
				cur.execute("INSERT INTO queue (dat_str) VALUES ('%s')" % data_wo_crc)
				conn.commit()
                        	LOG("inserted row")

				neodisplay(hub_home, 'pulldata_signal', data_wo_crc)

			else:
                        	LOG("crc doesnt match")
				
except KeyboardInterrupt:
	LOG("KeyboardInterrupt")
finally:
        ser.close()
	conn.close();
	flog.close();
	GPIO.cleanup()

