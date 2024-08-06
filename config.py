import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

SQLALCHEMY_TRACK_MODIFICATIONS = False
# Connect to local database URL:
# in this case the database is called 'project1' and the local login credentials are provided.
# dialect is 'PostgreSQL' and the driver is 'psycopg2'.
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:Biosphere4212!@localhost:5432/project1'
