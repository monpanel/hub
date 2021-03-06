
import os
import sqlite3 as lite 
import commands as sp
import time
import ConfigParser
from monutils import neodisplay

hub_home=os.environ.get('HUB_HOME', '/opt/monpanel.com/hub/prod')

conn = None
conn = lite.connect(hub_home + '/dat/local.db') 
cur = conn.cursor() 

flog=open(hub_home + '/log/rttmon.log', 'w+')

def LOG(str):
	flog.write(str);
	flog.write("\n");
	flog.flush();

def ping():
	rtt = -1;
	status,result = sp.getstatusoutput("ping -q -W 1 -c 10 8.8.8.8")
	if status == 0:
		status,result = sp.getstatusoutput("echo '" + str(result) + "' |tail -1 |cut -d '/' -f5")
		rtt = int(float(result))
		LOG("AVG rtt=" + str(rtt))
	else:
		LOG("Internet connection is DOWN!")

	return rtt

# main

neodisplay(hub_home, 'rttmon_start', 'dummy')

try:
        config = ConfigParser.ConfigParser()
        config.read(hub_home + "/dat/" + "hub.ini")
        SID = config.get("rttmon", "SID")
except Exception as e:
        LOG(str(e))
        raise e

LOG("SID = " + SID)


try:
	while 1:
		rtt = ping()
		if rtt > 0:
			val = SID + ":rtt=" + str(rtt)
			cur.execute("INSERT INTO queue (dat_str) VALUES ('%s')" % val)
			conn.commit()
			LOG("inserted row")
			neodisplay(hub_home, 'rttmon_signal', str(rtt))
		
		time.sleep(60)
				
except KeyboardInterrupt:
	LOG("KeyboardInterrupt")
finally:
	conn.close();
	flog.close();

