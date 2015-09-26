import sqlite3

def get_connection():
	return sqlite3.connect('HackathonDB.db')

def get_job(DB_connection,position_lat,position_lon,target_lat,target_lon):

	min_dist = None
	job_id = None
	for row in DB_connection.execute('SELECT * FROM jobs').fetchall():
		ID, job_position_lat, job_position_lon, job_target_lat, job_target_lon, _ = row
		cur_dist = (target_lat - job_target_lat)**2 + (target_lon - job_target_lon)**2
		if min_dist:
			if min_dist > cur_dist:
				min_dist = cur_dist
				job_id = ID
		else:
			min_dist = cur_dist
			job_id = ID

	_, job_position_lat, job_position_lon, job_target_lat, job_target_lon, _ = DB_connection.execute('SELECT * FROM jobs WHERE ID = '+str(job_id)).fetchone()

	return job_position_lat, job_position_lon, job_target_lat, job_target_lon
