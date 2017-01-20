"""Module with default settings to napps-server."""
import os
import redis

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the Database Connection - We are working with REDIs
HOST = '127.0.0.1'
PORT = '6379'
DB = '0'

DB_CON = redis.StrictRedis(host=HOST, port=PORT, db=DB, charset="utf-8",
                           decode_responses=True)

# Define NAPPS_SERVER CONFIGURATION
NAPPS_SERVER_HOST = '127.0.0.1'
NAPPS_SERVER_PORT = '5000'

NAPPS_SERVER_URL = 'http://{}:{}'.format(NAPPS_SERVER_HOST, NAPPS_SERVER_PORT)
