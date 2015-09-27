import sqlite3
import Jobmatching

def get_connection():

	return sqlite3.connect('HackathonDB.db')

def get_closest_bikes(db_connection, position_lat, position_lon, target_lat, target_lon, number_of_bikes = 10, radius = 0.5):
	print 'interface gives back ', position_lat, position_lon, target_lat, target_lon
	return Jobmatching.get_closest_bikes(db_connection, \
			 Jobmatching.Driver(position_lat, position_lon, target_lat, target_lon, number_of_bikes, radius))

