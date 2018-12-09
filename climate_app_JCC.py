import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
from flask import Flask, jsonify
from dateutil.relativedelta import relativedelta as rd

### Hawaii Climate App Purpose: This application provides climate data for Hawaii. 
## The `/api/v1.0/precipitation` route returns precipitation values for all dates
#  in the database as a JSON representation of a dictionary. 
## The `/api/v1.0/stations` route returns a JSON list of all stations from the database.
## The `/api/v1.0/tobs` route returns dates and temp observations for the previous year.
## The `/api/v1.0/<start>` route returns a JSON list of the min, avg, and max temp for a
#  given start date and all subsequent dates in the database.
## The `/api/v1.0/<start>/<end>` route returns a JSON list of the min, avg, and max temp
#  for all dates greater than or equal to the user-input start date and less than or equal
#  to the user-input end date.
## The '/api/v1.0/text/<start>' route returns prettier JSON verbiage of the 
# min, avg, and max temp for a user-input start date and all subsequent dates in the database.
## The `/api/v1.0/text/<start>/<end>` route returns prettier JSON verbiage of the min, avg, and max temp
#  for all dates greater than or equal to the user-input start date and less than or equal
#  to the user-input end date.
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""

        # Calculate latest date
    latest_date = session.query(func.max(Measurement.date)).all()
    latest_date = list(np.ravel(latest_date))
    latest_date = ''.join(latest_date)

    # Calculate oldest date
    oldest_date = session.query(func.min(Measurement.date)).all()
    oldest_date = list(np.ravel(oldest_date))
    oldest_date = ''.join(oldest_date)

    return (
        f"Welcome to the Hawaii Climate API, powered by Flask!<br/>"
        f"<br/>"
        f"This API provides historical climate data about Hawaii for research purposes, such as travel planning.<br/>"
        f"<br/>"
        f"The current date range contained in our database is {oldest_date} to {latest_date}.<br/>"
        f"The API routes will accept date values within that range and format. Please check back for updated data.<br/>"
        f"<br/>"
        f"Available API Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Returns a json dictionary representation of dates with precipitation values<br/>"
        f"Example Query URL: <a href='http://localhost:5000/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"Returns a json list of Hawaii weather stations IDs<br/>"
        f"Example Query URL: <a href='http://localhost:5000/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Returns a json list of Temp. Observations for the previous year from last data point<br/>"
        f"Example Query URL: <a href='http://localhost:5000/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"Returns a json list of the min, avg, and max temps for a range of dates greater than or equal to the start date<br/>"
        f"Example Query URL: <a href='http://localhost:5000/api/v1.0/2010-01-01'>/api/v1.0/2010-01-01</a><br/>"
        f"<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
        f"Returns a json list of the min, avg, and max temps for a range of dates greater than or equal to the start date and less than or equal to the<br/>\
        end date<br/>"
        f"Example Query URL: <a href='http://localhost:5000/api/v1.0/2010-01-01/2010-02-01'>/api/v1.0/2010-01-01/2010-02-01</a><br/>"
        f"<br/>"
        f"/api/v1.0/text/YYYY-MM-DD<br/>"
        f"Returns a human-readable json printout of the min, avg, and max temps for a range of dates greater than or equal to the start date<br/>"
        f"Example Query URL: <a href='http://localhost:5000/api/v1.0/text/2010-01-01'>/api/v1.0/text/2010-01-01</a><br/>"
        f"<br/>"
        f"/api/v1.0/text/YYYY-MM-DD/YYYY-MM-DD<br/>"
        f"Returns a human-readable json printout of the min, avg, and max temps for a range of dates greater than or equal to the start date and less than<br/>\
        or equal to the end date<br/>"
        f"Example Query URL: <a href='http://localhost:5000/api/v1.0/text/2010-01-01/2010-02-01'>/api/v1.0/text/2010-01-01/2010-02-01</a><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a json dictionary representation of dates with precipitation values"""
    # Query all dates and all prcp measurements
    results_dates = session.query(Measurement.date).all()
    results_prcp = session.query(Measurement.prcp).all()

    # Convert lists of tuples into normal lists, then into a dictionary
    keys_dates = list(np.ravel(results_dates))
    values_prcp = list(np.ravel(results_prcp))
    all_precip = dict(zip(keys_dates, values_prcp))
    
    #Jsonify results
    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return a json list of Hawaii weather station IDs"""
    # Query all station IDs
    results_stations = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results_stations))

    # jsonify results
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a json list of Temp. Observations for the previous year 
    from last data point"""
    # Calculate start and end dates
    latest_date = session.query(func.max(Measurement.date)).all()
    latest_date = list(np.ravel(latest_date))
    latest_date = ''.join(latest_date)
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')

    one_year_ago = latest_date + rd(years=-1, days=-1)
    one_year_ago

    # Define function
    def calc_temps(one_year_ago, latest_date):
        """TMIN, TAVG, and TMAX for a list of dates.
        Args:
        one_year_ago (string): A date string in the format %Y-%m-%d
        latest_date (string): A date string in the format %Y-%m-%d
        Returns:
        TMIN, TAVE, and TMAX
        """
        # query for dates and tobs; if tobs only are desired, 
        # remove Measurement.date from session.query input)
        return session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date >= one_year_ago).filter(Measurement.date <= latest_date).all()

    # Query dates and temp. obs. for a year from last data point in DB
    calculated_temps = calc_temps(one_year_ago, latest_date)

    # jsonify results
    return jsonify(calculated_temps)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a json list of the min, avg, and max temps for a range of dates
    greater than or equal to the start date"""

    # Calculate all dates in database and convert tuples to list
    all_dates = session.query(Measurement.date).all()
    all_dates = list(np.ravel(all_dates))

    # Calculate latest date
    latest_date = session.query(func.max(Measurement.date)).all()
    latest_date = list(np.ravel(latest_date))
    latest_date = ''.join(latest_date)

    # Calculate oldest date
    oldest_date = session.query(func.min(Measurement.date)).all()
    oldest_date = list(np.ravel(oldest_date))
    oldest_date = ''.join(oldest_date)

    # Create If else statement to ensure input date is contained in database and to notify user if needed
    if start in all_dates:
        start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
        return jsonify(start_data)

    else: 
        return jsonify("error: " f"{start} start date not found in database; please enter date between {oldest_date} and {latest_date}")

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a json list of the min, avg, and max temps for a range of dates
    greater than or equal to the start date and less than or equal to the
    end date"""

    # Calculate all dates in database and convert tuples to list
    all_dates = session.query(Measurement.date).all()
    all_dates = list(np.ravel(all_dates))

    # Calculate latest date
    latest_date = session.query(func.max(Measurement.date)).all()
    latest_date = list(np.ravel(latest_date))
    latest_date = ''.join(latest_date)

    # Calculate oldest date
    oldest_date = session.query(func.min(Measurement.date)).all()
    oldest_date = list(np.ravel(oldest_date))
    oldest_date = ''.join(oldest_date)

    # Create If else statement to ensure input dates are contained in database and to notify user if needed
    ## I thought about adding a statement to check if the end date was later than the start date, but for the purposes of
    ## this analysis I think a power user using JSON lists would want to know they made a mistake. That said, for the text
    ## printout version below, I included a swap while also notifying the user for future reference. 

    if start > end:
        return jsonify(f"start date ({start}) is greater than end date ({end}), please choose a start date less than end date between {oldest_date} and {latest_date}")
        
    elif start in all_dates and end in all_dates: 
        start_end_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).filter(and_\
        (Measurement.date >= start, Measurement.date <= end)).all()

        return jsonify(start_end_data)

    elif start not in all_dates and end in all_dates: 
        return jsonify("error: " f"{start} (start date) not found in database; please enter date between {oldest_date} and {latest_date}")

    elif start in all_dates and end not in all_dates: 
        return jsonify("error: " f"{end} (end date) not found in database; please enter date between {oldest_date} and {latest_date}")

    else: 
        return jsonify("error: " f"{start} (start date) and {end} (end date) not found in database; please enter dates between {oldest_date} and {latest_date}")


@app.route("/api/v1.0/text/<start>")
def start_text(start):
    """Return a human-readable json printout of the min, avg, and max temps for a range of dates
    greater than or equal to the start date"""

    # Calculate all dates in database and convert tuples to list
    all_dates = session.query(Measurement.date).all()
    all_dates = list(np.ravel(all_dates))

    # Calculate latest date
    latest_date = session.query(func.max(Measurement.date)).all()
    latest_date = list(np.ravel(latest_date))
    latest_date = ''.join(latest_date)

    # Calculate oldest date
    oldest_date = session.query(func.min(Measurement.date)).all()
    oldest_date = list(np.ravel(oldest_date))
    oldest_date = ''.join(oldest_date)

    # Create If else statement to ensure input date is contained in database and to notify user if needed
    if start in all_dates:
        start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
        return jsonify(f"date range: from {start} (start) to {latest_date} (latest date), temperature results (Min, Avg, Max [Fahrenheit]): {start_data}")

    else: 
        return jsonify("error: " f"{start} start date not found in database; please enter date between {oldest_date} and {latest_date}")

@app.route("/api/v1.0/text/<start>/<end>")
def start_end_text(start, end):
    """Return a human-readable json printout of the min, avg, and max temps for a range of dates
    greater than or equal to the start date and less than or equal to the
    end date"""

    # Calculate all dates in database and convert tuples to list
    all_dates = session.query(Measurement.date).all()
    all_dates = list(np.ravel(all_dates))

    # Calculate latest date
    latest_date = session.query(func.max(Measurement.date)).all()
    latest_date = list(np.ravel(latest_date))
    latest_date = ''.join(latest_date)

    # Calculate oldest date
    oldest_date = session.query(func.min(Measurement.date)).all()
    oldest_date = list(np.ravel(oldest_date))
    oldest_date = ''.join(oldest_date)

    # Create If else statement to swap dates if inserted backward, and to ensure input dates are contained in database and to notify user if needed

    if start > end:
        #return jsonify(f"start date ({start}) is greater than end date ({end}), please choose a start date less than end date between {oldest_date} and {latest_date}")
        start1 = end
        end1 = start
        start_end_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).filter(and_\
        (Measurement.date >= start1, Measurement.date <= end1)).all()
        return jsonify(f"Your start date {start} was larger than your end date {end}, so we swapped them ;) Temperature results (Min, Avg, Max [Fahrenheit]): {start_end_data}")

    elif start in all_dates and end in all_dates: 
        start_end_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).filter(and_\
        (Measurement.date >= start, Measurement.date <= end)).all()
        return jsonify(f"start date: {start}, end date: {end}, temperature results (Min, Avg, Max [Fahrenheit]): {start_end_data}")

    elif start not in all_dates and end in all_dates: 
        return jsonify("error: " f"{start} (start date) not found in database; please enter date between {oldest_date} and {latest_date}")

    elif start in all_dates and end not in all_dates: 
        return jsonify("error: " f"{end} (end date) not found in database; please enter date between {oldest_date} and {latest_date}")

    else: 
        return jsonify("error: " f"{start} (start date) and {end} (end date) not found in database; please enter dates between {oldest_date} and {latest_date}")

if __name__ == '__main__':
    app.run(debug=True)
