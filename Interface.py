import sqlite3

class Location:

	def __init__(latitude,longitude):
		self.latitude = latitude
		self.longitude = longitude

class Client:

	def __init__(position,target):
		self.position = position
		self.target = target

class Job(Client):
	
	def __init__(ID,position,target,date):
		super(Job).__init__(position,target)
		self.ID = ID
		self.date = date

def get_job(row):
	try:
		return Job(row[0],Location(row[1],row[2]),Location(row[3],row[4]),row[5])
	except IndexError:
		raise IndexError
	

def get_connection():
	return sqlite3.connect('HackathonDB.db')

def get_distance(location1, location2):
	return (location1.latitude - location2.latitude)**2 + (location1.longitude - location2.longitude)**2

def get_current_job_value(client,job):
	return get_distance(client.target,job.target)

def get_job(DB_connection,position_lat,position_lon,target_lat,target_lon):

	client = Client(Location(position_lat,position_lon),Location(target_lat,target_lon))
	best_job_value = None
	best_job = None

	for row in DB_connection.execute('SELECT * FROM jobs').fetchall():
		job = get_job(row)
		cur_job_value = get_current_job_value(client,job)

		if best_job_value:
			if best_job_value > cur_job_value:
				best_job_value = cur_job_value
				best_job = job
		else:
			best_job_value = cur_job_value
			best_job = job

	return best_job.position.latitude, best_job.position.longitude, best_job.target.latitude, best_job.target.longitude

