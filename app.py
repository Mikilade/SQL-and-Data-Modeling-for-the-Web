"""Application code for the Fyyur App."""
#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate # Migrate import
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)



moment = Moment(app)
app.config.from_object('config')

# init database
db.init_app(app)

# Setup migration to local db
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  """Pre-built datetime formatting function."""
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  """Display all venues."""

  # get local time
  current_time = datetime.now()

  # initialize areas dict
  areas = {}

  # query all venues
  venues = Venue.query.all()

  for venue in venues:
     # filter shows by a corresponding venue ID and if the start time is upcoming (in the future), then count
     upcoming_shows_count = Show.query.filter(Show.venue_id == venue.id, Show.start_time > current_time).count()
     
     # define the venue data
     venue_data = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": upcoming_shows_count
     }
     
     # define the location, combination of city and state for unique identifier
     location = f'{venue.city}, {venue.state}'

     # if the location isn't in the area dict, add it and make the current venue the first venue in its venues list
     if location not in areas:
        areas[location] = {
           "city": venue.city,
           "state": venue.state,
           "venues": [venue_data]
        }
     # if it IS in the area dict, append this venue to the venues list
     else:
        areas[location]["venues"].append(venue_data)

  data = list(areas.values())

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  """Search for specific venues."""
  search_term = request.form.get('search_term', '')

  # Partial string search with SQLAlchemy. Filters a query from the Venue table using partial string search.
  # Returns all results.
  search_results = Venue.query.filter(
     Venue.name.ilike(f'%{search_term}%')
  ).all()

  # Create response dict. Count number of venue hits then initialize empty data list.
  response = {
     'count': len(search_results),
     'data': []
  }

  # Get current time
  current_time = datetime.now()

  # filter shows by a corresponding venue ID and if the start time is upcoming (in the future), then count
  for venue in search_results:
     num_upcoming_shows = Show.query.filter(
        Show.venue_id == venue.id,
        Show.start_time > current_time
     ).count()

     response["data"].append(
        {
           'id': venue.id,
           'name': venue.name,
           'num_upcoming_shows': num_upcoming_shows
        }
     )

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  """Show venue details for a given venue."""
  
  # Query venue from Venue table using given ID
  venue = Venue.query.get(venue_id)

  # Handle if a venue wasn't supplied properly
  if not venue:
     return render_template('errors/404.html'), 404
  
  # Grab current time
  current_time = datetime.now()

  # Query past and future shows by filtering based on time comparison to current
  past_shows_data = []
  upcoming_shows_data = []

  for show in venue.shows:
     queried_show = {
           'artist_id': show.artist_id,
           'artist_name': show.artist.name,
           'artist_image_link': show.artist.image_link,
           'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
      }
     if show.start_time < current_time:
        past_shows_data.append(queried_show)
     else:
        upcoming_shows_data.append(queried_show)
  
  # Construct data dict for template
  data = {
     'id': venue.id,
     'name': venue.name,
     'genres': [genre for genre in venue.genres],
     'address': venue.address,
     'city': venue.city,
     'state': venue.state,
     'phone': venue.phone,
     'website': venue.website_link,
     'facebook_link': venue.facebook_link,
     'seeking_talent': venue.looking_for_talent,
     'seeking_description': venue.seeking_description,
     'image_link': venue.image_link,
     'past_shows': past_shows_data,
     'upcoming_shows': upcoming_shows_data,
     'past_shows_count': len(past_shows_data),
     'upcoming_shows_count': len(upcoming_shows_data)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  """Pre-built function. Create venue form."""
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  """Create the venue submission and add it to the DB."""

  form = VenueForm(request.form)

  # check form validation
  if form.validate():
    try:
      # Populate a new Venue object with captured form data
      new_venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        website_link = form.website_link.data,
        looking_for_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
      )
      # Add the new venue to the ongoing session
      db.session.add(new_venue)
      # Commit the session to the database to really save it
      db.session.commit()
      # Flash the success message
      flash('Venue ' + new_venue.name + ' was successfully listed!')
    except Exception as e:
      # Rollback the session, an error occurred
      db.session.rollback()
      # Flash the error message
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
      # Debugging statement to capture the exception
      print(f'The following exception occurred: {e}')
    finally:
      # Close the session once everything is done.
      db.session.close()
  # if invalid field
  else:
     message = []
     for field, errors in form.errors.items():
        for error in errors:
           message.append(f'{field}: {error}')
     flash('Please fix the following errors: ' + ', '.join(message))
     form = VenueForm()
     return render_template('forms/new_venue.html', form=form) 

  return render_template('pages/home.html') # Redirect to homepage

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  """Delete a venue given an ID."""
  # Bonus challenge was not completed in the interest of time.

  try:
     # Query the venue by given ID
     venue = Venue.query.get(venue_id)

     if not venue:
        flash(f'Venue ID {venue_id} does not exist.')
        return render_template('pages/home.html')
     
     # Delete the venue entry from the Venue table in the database
     db.session.delete(venue)
     db.session.commit()

     # Flash deletion success message
     flash(f'Venue {venue.name} was successfully deleted!')
  
  except Exception as e:
     # Rollback session if an error occurred.
     db.session.rollback()
     # Flash error message
     print(f'The following exception occurred: {e}')
  finally:
     # Close session
     db.session.close()
  
  # Redirect to homepage post deletion

  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  """Display all artists."""
  artists = Artist.query.all()

  # Populate 'data' as a list of dictionaries
  data = [
     {
        'id': artist.id,
        'name': artist.name
     } for artist in artists
  ]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')

  # Partial string search with SQLAlchemy. Filters a query from the Artist table using partial string search.
  # Returns all results.
  search_results = Artist.query.filter(
     Artist.name.ilike(f'%{search_term}%')
  ).all()

  # Create response dict. Count number of artist hits then initialize empty data list.
  response = {
     'count': len(search_results),
     'data': []
  }

  # Calculate current time
  current_time = datetime.now()

  # filter shows by a corresponding artist ID and if the start time is upcoming (in the future), then count
  for artist in search_results:
     num_upcoming_shows = Show.query.filter(
        Show.artist_id == artist.id,
        Show.start_time > current_time
     ).count()

     response["data"].append(
        {
           'id': artist.id,
           'name': artist.name,
           'num_upcoming_shows': num_upcoming_shows
        }
     )
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term'))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  """Show details for a specific ID."""
  # query the Artist from the Artist table by artist_id
  artist = Artist.query.get(artist_id)

  # Flash an error if bad input was given
  if not artist:
     flash(f'Artist ID {artist_id} does not exist.')
     return render_template('errors/404.html'), 404
  
  # Calc current time
  current_time = datetime.now()

  # Query past and future shows by filtering based on time comparison to current
  past_shows_data = []
  upcoming_shows_data = []

  for show in artist.shows:
     queried_show = {
           'venue_id': show.venue_id,
           'venue_name': show.venue.name,
           'venue_image_link': show.venue.image_link,
           'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
      }
     if show.start_time < current_time:
        past_shows_data.append(queried_show)
     else:
        upcoming_shows_data.append(queried_show)
  
  # Construct data dict for template
  data = {
     'id': artist.id,
     'name': artist.name,
     'genres': [genre for genre in artist.genres],
     'city': artist.city,
     'state': artist.state,
     'phone': artist.phone,
     'website': artist.website_link,
     'facebook_link': artist.facebook_link,
     'seeking_venue': artist.looking_for_venues,
     'seeking_description': artist.seeking_description,
     'image_link': artist.image_link,
     'past_shows': past_shows_data,
     'upcoming_shows': upcoming_shows_data,
     'past_shows_count': len(past_shows_data),
     'upcoming_shows_count': len(upcoming_shows_data)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  """Edit artist details given an ID."""

  # Query artist by artist_id
  artist = Artist.query.get(artist_id)

  if not artist:
     flash(f'Artist ID {artist_id} does not exist.')
     return render_template('errors/404.html'), 404
  
  # Create and pre-populate form with artist's data
  form = ArtistForm(obj=artist)

  # Populate the artist data for the template
  artist_data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_for_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }

  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # query artist with artist_id from Artist table
  artist = Artist.query.get(artist_id)

  # Handle if artist ID DNE
  if not artist:
     flash(f'Artist ID {artist_id} does not exist.')
     return render_template('errors/404.html'), 404
  
  # Create a form object from submitted data
  form = ArtistForm(request.form)

  try:
     # Update artist with form data
     artist.name = form.name.data
     artist.genres = form.genres.data
     artist.city = form.city.data
     artist.state = form.state.data
     artist.phone = form.phone.data
     artist.website = form.website_link.data
     artist.facebook_link = form.facebook_link.data
     artist.looking_for_venue = form.seeking_venue.data
     artist.seeking_description = form.seeking_description.data
     artist.image_link = form.image_link.data

     # Save changes to db
     db.session.commit()
     flash(f'{artist.name} was successfully updated!')
  except Exception as e:
     # rollback session if an error occurred
     db.session.rollback()
     flash(f'An error has occurred. Artist {artist.name} was not updated.')
     # dump exception information for debugging
     print(f"Exception: {e}")
  finally:
     # close session to cleanup
     db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  """Edit venue details given an ID."""
  # query venue by ID
  venue = Venue.query.get(venue_id)

  # Flash an error if bad ID was given
  if not venue:
     flash(f'Venue ID {venue_id} does not exist.')
     return render_template('errors/404.html'), 404

  # Create form and pre-populate with queried venue data
  form = VenueForm(obj=venue)

  # Populate data dict to pass to template
  data = {
     'id': venue.id,
     'name': venue.name,
     'genres': venue.genres,
     'address': venue.address,
     'city': venue.city,
     'state': venue.state,
     'phone': venue.phone,
     'website': venue.website_link,
     'facebook_link': venue.facebook_link,
     'seeking_talent': venue.looking_for_talent,
     'seeking_description': venue.seeking_description,
     'image_link': venue.image_link
  }

  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  """Save venue edits to the DB."""

  # Query venue by ID
  venue = Venue.query.get(venue_id)

  # Flash an error if bad ID was given
  if not venue:
     flash(f'Venue ID {venue_id} does not exist.')
     return render_template('errors/404.html'), 404
  
  # Create form with submitted data
  form = VenueForm(request.form)
     
  try:
     # Update venue with form data
     venue.name = form.name.data
     venue.genres = form.genres.data
     venue.address = form.address.data
     venue.city = form.city.data
     venue.state = form.state.data
     venue.phone = form.phone.data
     venue.website_link = form.website_link.data
     venue.facebook_link = form.facebook_link.data
     venue.looking_for_talent = form.seeking_talent.data
     venue.seeking_description = form.seeking_description.data
     venue.image_link = form.image_link.data

     # Save changes
     db.session.commit()
     flash(f'Venue {venue.name} was successfully updated!')
  except Exception as e:
     # Abort changes if an error occurred
     db.session.rollback()
     flash(f'An error has occurred. Venue {venue.name} was not updated.')
     # Dump exception info for debugging
     print(f'Exception: {e}')
  finally:
     # Close session to cleanup
     db.session.close()
     
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  """Pre-built function. Designs the create artist form."""
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    """Save the new artist details to the db."""
  # called upon submitting the new artist listing form
    form = ArtistForm(request.form)
    if form.validate():
      try:
        # Populate a new artist object with captured form data
        new_artist = Artist(
          name = form.name.data,
          city = form.city.data,
          state = form.state.data,
          phone = form.phone.data,
          genres = form.genres.data,
          facebook_link = form.facebook_link.data,
          image_link = form.image_link.data,
          website_link = form.website_link.data,
          looking_for_venues = form.seeking_venue.data,
          seeking_description = form.seeking_description.data
        )
        # Add the new venue to the ongoing session
        db.session.add(new_artist)
        # Commit the session to the database to really save it
        db.session.commit()
        # Flash the success message
        flash('Artist ' + new_artist.name + ' was successfully listed!')
      except Exception as e:
        # Rollback the session, an error occurred
        db.session.rollback()
        # Flash the error message
        flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
        # Debugging statement to capture the exception
        print(f'The following exception occurred: {e}')
      finally:
        # Close the session once everything is done.
        db.session.close()
    # if invalid field
    else:
      message = []
      for field, errors in form.errors.items():
          for error in errors:
            message.append(f'{field}: {error}')
      flash('Please fix the following errors: ' + ', '.join(message))
      form = ArtistForm()
      return render_template('forms/new_artist.html', form=form) 

    return render_template('pages/home.html') # Redirect to homepage


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  """Display all shows."""
  # Query all shows
  shows = Show.query.all()

  # Intialize empty list of dictionaries
  data = []
  for show in shows:
     # query the venue and artist from the show data
     venue = Venue.query.get(show.venue_id)
     artist = Artist.query.get(show.artist_id)
     # Construct the show_data dict
     show_data = {
        'venue_id': show.venue_id,
        'venue_name': venue.name,
        'artist_id': show.artist_id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
     }
     data.append(show_data)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  """Pre-built function. Creates the ShowForm form."""
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  """Save new show to the DB."""
  # Create a form from input data
  form = ShowForm(request.form)
  if form.validate():
    try:
      # Query the Artist and Venue with the specified IDs. Throw an exception if not found.
      artist = Artist.query.get(form.artist_id.data)
      if not artist:
          raise ValueError(f'Artist ID {form.artist_id.data} does not exist.')

      # Check if the venue_id exists in the Venue table
      venue = Venue.query.get(form.venue_id.data)
      if not venue:
          raise ValueError(f'Venue ID {form.venue_id.data} does not exist.')

      # Create the new show object for insert into db
      new_show = Show(
          artist_id = form.artist_id.data,
          venue_id = form.venue_id.data,
          start_time = form.start_time.data
      )
      # Add and commit to db
      db.session.add(new_show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    except Exception as e:
      # Abort the session, an exception has occurred
      db.session.rollback()
      # Flash an error message and dump the exception for debugging
      flash('An error occurred. Show could not be listed.')
      print(f'Exception occurred: {e}')
    finally:
      # Clean up and close session
      db.session.close()
  # if invalid field
  else:
     message = []
     for field, errors in form.errors.items():
        for error in errors:
           message.append(f'{field}: {error}')
     flash('Please fix the following errors: ' + ', '.join(message))
     form = ShowForm()
     return render_template('forms/new_show.html', form=form) 

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
