#

import os
import sqlite3 as lite 
import re
import time
import urllib2
import urlparse
import socket
import json
import ConfigParser
from monutils import neodisplay


BASE_URL = 'https://pmon.mpcld.com'
SIGNIN_URL = urlparse.urljoin(BASE_URL, '/api/v1/cmod/signin/')
BATCH_CREATION_URL = urlparse.urljoin(BASE_URL, '/api/v1/datapoint/batch_creation/')

hub_home=os.environ.get('HUB_HOME', '/opt/monpanel.com/hub/prod')
MP_API_HOSTNAME = "pmon.mpcld.com"
hostname = MP_API_HOSTNAME

flog=open(hub_home + '/log/pushdata.log', 'w+', 0)

conn = None
token = None
all_rows = []

def LOG(str):
        flog.write(str);
        flog.write("\n");
        flog.flush();

def encodeUserData(user, password):
    return "Basic " + (user + ":" + password).encode("base64").rstrip()


#
# get token from the server 
def get_token():
	LOG("get_token")

	global token

	#curl -m 20 -s -H "Content-Type: application/json" -X POST --data '{"cid": "MDF5-24SD", "secure_key": "KJ73"}' "http://pmon.mpcld.com/api/v1/cmod/signin/"
	u='username'
	p='userpass'
	url='https://pmon.mpcld.com/api/v1/cmod/signin/'

	req = urllib2.Request(url)
	req.get_method = lambda: "POST"
	req.add_header('Accept', 'application/json')
	req.add_header("Content-type", "application/json")
	#req.add_header('Authorization', encodeUserData(u, p))
	#data = urllib.urlencode({"cid": "MDF5-24SD", "secure_key": "KJ73"})
	data = json.dumps({"cid": CID, "secure_key": SECURE_KEY})

	try:
		res = urllib2.urlopen(req, data = data, timeout = 20)
		token = res.read()
		LOG("token = %s" % token)
	except socket.timeout, e:
		LOG(str(e))
		raise e
	except urllib2.HTTPError,e:
		LOG(str(e))
		raise e



def local_data_array_to_api_dict(data, cid):
    """
    Convert array like [505, '2015-03-06 03:42:56', 'TU12-9K78:t=21:h=34:v=3.5:c=14:s=-55'] 
    to dict {"cid":cid, "sid": "TU12-9K78", "svalue":"t=21:h=34:v=3.5:c=14:s=-55", "reg_ts":"2015-03-06T03:42:56"},
    which can be passed to the endpoint.
    """
    d = {'cid': cid}
    ary = data[2].split(':')
    d['sid'] = ary[0]
    d['svalue'] = ':'.join(ary[1:])
    d['reg_ts'] = data[1].replace(' ', 'T') + 'Z'
    
    return d


#
# fetch data from the queue 
def get_data(numrows = 10):
	LOG("get_data")

	global all_rows
	try:
		cur = conn.cursor() 
		cur.execute("SELECT rowid, reg_dt, dat_str FROM (SELECT rowid, reg_dt, dat_str FROM queue ORDER BY 2 ASC) LIMIT " + str(numrows))
		all_rows = cur.fetchall()
	except Exception as e:
		LOG(str(e))
		raise e
	finally:
		cur.close() 

#
# send data to server 
def put_data():
	LOG("put_data")

	global all_rows
	try:
		req = urllib2.Request(BATCH_CREATION_URL)
		req.get_method = lambda: "POST"
		req.add_header('Accept', 'application/json')
		req.add_header("Content-type", "application/json")
		req.add_header('Authorization', 'ApiKey %s:%s' % (CID, token))

		objects = [local_data_array_to_api_dict(data, CID) for data in all_rows]
		data = json.dumps({'objects': objects})
		LOG('\r\n>>>')
		LOG(data)

		res = urllib2.urlopen(req, data = data, timeout = 20)
		if res.getcode() != 202:
			LOG('\r\n<<<')
			LOG(str(res.getcode()))
			raise Exception('urlopen', str(res.getcode()))

	except Exception as e:
		LOG(str(e))
		raise e
#	finally:

#
# remove data from the queue
def del_data():
	LOG("del_data")

	global all_rows
	try:
		cur = conn.cursor() 
		for row in all_rows:
			LOG('Deleting: %d: %s %s' % (row[0], row[1], row[2], ))
			cur.execute("DELETE FROM queue WHERE rowid = ?", (row[0],))
		conn.commit()
	except Exception as e:
		LOG(str(e))
		conn.rollback()
		raise e
	finally:
		cur.close() 

#
# main
 
neodisplay(hub_home, 'pushdata_start', 'dummy')

try:
	config = ConfigParser.ConfigParser()
	config.read(hub_home + "/dat/" + "hub.ini")
	CID = config.get("module", "CID")
	SECURE_KEY = config.get("module", "SECURE_KEY")
except Exception as e:
	LOG(str(e))
	raise e

LOG("CID = " + CID)
LOG("SECURE_KEY = " + SECURE_KEY)


while 1:
	try:
		response = os.system("ping -c 1 " + hostname + " > /dev/null 2>&1")
		if response != 0:
			LOG("ERROR: host %s is not available" % hostname)
			time.sleep(2)
			continue

		if token is not None: 
			LOG("Using old token: %s" % token)
		else:
			get_token() 

		conn = lite.connect(hub_home + '/dat/local.db') 
		all_rows = []

		get_data()
		if len(all_rows) == 0:
			LOG("Queue is empty. waiting 5 sec..")
			time.sleep(5)
			continue
		time.sleep(1)

		put_data()
		time.sleep(1)

		del_data()
		time.sleep(1)
		LOG(" ")

		time.sleep(2)

	except Exception as e:
		LOG(str(e))
		if conn is not None: 
			conn.close()
		time.sleep(60)
	finally:
		if conn is not None: 
			conn.close()

	time.sleep(10)

