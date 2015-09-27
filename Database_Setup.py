import sqlite3
from random import random
from datetime import datetime,timedelta

conn = sqlite3.connect('HackathonDB.db')

NUMBER_OF_JOBS = 2000
NUMBER_OF_BIKES = 10000

try:
	conn.execute('DROP TABLE jobs')
	conn.execute('DROP TABLE bikes')
except:
	print 'no tables to drop.'

conn.execute('CREATE TABLE 	jobs(ID int(32), \
							target_lat float(32), \
							target_lon float(32), \
							time date(32), \
							bikeID int(32), FOREIGN KEY(bikeID) REFERENCES bikes(ID))')

conn.execute('CREATE TABLE 	bikes(ID int(32), \
							position_lat float(32), \
							position_lon float(32), \
							active_job boolean)')

west = 13.25
east = 13.5
north = 52.56
south = 52.45

for i in range(NUMBER_OF_BIKES):
	position_lat = south + (north - south)*random()
	position_lon = west + (east - west)*random()

	conn.execute('INSERT INTO bikes VALUES(?,?,?,?)', (i, position_lat, position_lon, False))

for i in range(NUMBER_OF_JOBS):
	target_lat = south + (north - south)*random()
	target_lon = west + (east - west)*random()
	
	time = datetime(2015,9,26,8) + timedelta(seconds=random()*60*60*4)
	bikeID = conn.execute('SELECT ID FROM bikes WHERE active_job = 0 ORDER BY RANDOM() LIMIT 1').fetchone()[0]

	conn.execute('INSERT INTO jobs VALUES(?,?,?,?,?)', (i, target_lat, target_lon, time, bikeID))
	conn.execute('UPDATE bikes SET active_job = 1 WHERE ID = ' + str(bikeID))

conn.commit()
conn.close()
