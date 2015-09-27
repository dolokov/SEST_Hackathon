'''
	Handle matching between drivers and jobs
'''

import math
from datetime import datetime

#MAX_WALKING_DISTANCE_PER_KM_DRIVING = 0.1
MAX_TIME_DELIVERY = 10
VALUE_PER_KM = 0.3
COST_PER_KM = 0.1

class Location(object):

	def __init__(self,latitude,longitude):
		self.latitude = latitude
		self.longitude = longitude

class Route(object):

	def __init__(self,position,target):
		self.position = position
		self.target = target

class Driver(Route):

	def __init__(self,position_lat,position_lon,target_lat,target_lon,number_of_bikes,radius):

		super(Driver,self).__init__(Location(position_lat,position_lon),Location(target_lat,target_lon))
		self.number_of_bikes = number_of_bikes
		self.radius = radius	

	def print_driver(self):

		print 'Driver from ('+str(self.position.latitude)+','+str(self.position.longitude)+') to ('\
					+str(self.target.latitude)+','+str(self.target.longitude)+'). Distance: '+str(get_distance(self.position,self.target))+ ' km. Current time: ' + str(datetime.now()) 

class Job(Route):
	
	def __init__(self,ID,position,target,timestamp_in,latest_arrival = None,value = 0):
		super(Job,self).__init__(position,target)
		self.timestamp_in = timestamp_in
		self.latest_arrival = latest_arrival
		
		self.distance = get_distance(self.target,self.position)
		self.value = value - self.distance * COST_PER_KM

	def set_current_value(self, driver):

		#is the job within the radius?

		walking_factor = get_distance(driver.position,self.position)/driver.radius
		if walking_factor > 1:
			self.value = 'false'

		else:
			
			effective_distance_achieved = self.distance - get_distance(driver.target,self.target)
			
			if not self.latest_arrival:
				time_factor = 1
			elif self.latest_arrival < datetime.now(): 
				time_factor = 3
			else:
				# print self.timestamp_in, self.latest_arrival, datetime.now()

				# print self.latest_arrival-self.timestamp_in
				# print self.latest_arrival-datetime.now()
				time_factor = 1 + 2*(1- (self.latest_arrival - datetime.now()).seconds*1.0/(self.latest_arrival-self.timestamp_in).seconds)**2

			self.value = max(effective_distance_achieved,0)*VALUE_PER_KM *time_factor - get_distance(self.position,driver.target) * COST_PER_KM

	def print_job(self):

		print 'Job from ('+str(self.position.latitude)+','+str(self.position.longitude)+') to ('\
					+str(self.target.latitude)+','+str(self.target.longitude)+') with value '+ str(self.value)\
					+'. Time_in: '+ str(self.timestamp_in)+', latest arrival: '+ str(self.latest_arrival)

def create_job(db_connection, row):
	try:
		position_lat, position_lon = db_connection.execute('SELECT position_lat, position_lon FROM bikes WHERE ID = '+str(row[5])).fetchone()
		current_location = Location(position_lat, position_lon)

		timestamp_in = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S.%f')
		latest_arrival = datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S.%f')

		job = Job(row[0],current_location,Location(row[1],row[2]),timestamp_in, latest_arrival)
		return job
	except IndexError:
		raise IndexError

def get_distance(location1, location2):

	# Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
         
    # phi = 90 - latitude
    phi1 = (90.0 - location1.latitude)*degrees_to_radians
    phi2 = (90.0 - location2.latitude)*degrees_to_radians
         
    # theta = longitude
    theta1 = location1.longitude*degrees_to_radians
    theta2 = location2.longitude*degrees_to_radians
     
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
 
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc*6373

def find_closest_empty(db_connection, driver):

	closest_bike = None
	distance = None
	for row in db_connection.execute('SELECT * FROM bikes WHERE active_job = 0').fetchall():
		
		current_bike_location = Location(row[1],row[2])
		current_distance = get_distance(driver.position, current_bike_location)

		if not distance:
			closest_bike = current_bike_location
			distance = current_distance
		elif distance > current_distance:
			closest_bike = current_bike_location
			distance = current_distance

	return closest_bike

def get_closest_bikes(db_connection, driver):

	best_job_value = 0

	bikes = [False]*driver.number_of_bikes

	for row in db_connection.execute('SELECT * FROM jobs').fetchall():
		job = create_job(db_connection, row)
		job.set_current_value(driver)

		if job.value != 'false': 
			i = 0
			while i < driver.number_of_bikes:
				if bikes[i]:
					if bikes[i].value < job.value:
						bikes = bikes[0:i] + [job] + bikes[i:(driver.number_of_bikes - 1)]
						i = driver.number_of_bikes
					else: 
						i = i + 1
				else:
					bikes[i] = job
					i = driver.number_of_bikes

	bikes = filter(lambda entry:entry, bikes)

	closest_empty = find_closest_empty(db_connection, driver)

	if closest_empty:
		bikes.append(Job(None,closest_empty,driver.target,datetime.now(),value = 0))

	return bikes
		