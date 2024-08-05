from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Venue(db.Model):
    """The Venue class is constructed from the Venue table within the local db."""
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(2)) # state is a two char string
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(200)) # increased no. of characters allowed here in case of long link

    # Implementation of missing fields
    genres = db.Column(db.ARRAY(db.String(120))) # Store genres as array of strings
    website_link = db.Column(db.String(200))
    looking_for_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500)) # allocate a good amount of characters for the seeking description

class Artist(db.Model):
    """The Artist class is constructed from the Artist table within the local db."""
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(2)) # state is a two char string
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120))) # modify genres to be an array of strings
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(200)) # increased no. of characters allowed here in case of long link

    # Implemention of missing fields
    website_link = db.Column(db.String(200))
    looking_for_venues = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500)) # allocate a good amount of characters for the seeking description

class Show(db.Model):
   """The Show class is constructed from the Show table within the local db."""
   __tablename__ = 'Show'

   id = db.Column(db.Integer, primary_key=True)
   start_time = db.Column(db.DateTime, nullable=False)
   artist_id = db.Column(db.Integer, nullable=False)
   venue_id = db.Column(db.Integer, nullable=False)