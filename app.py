
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Setting up the Database
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the database into our classes
Base = automap_base()

# Reflecting the database
Base.prepare(engine, reflect=True)

# Creating a variable for each of the classes so that we can reference them later
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session link from Python to our database
session = Session(engine)

# Defying Flask app
app = Flask(__name__)

# Dedying the welcome route
@app.route("/")

# Creating welcome function
def welcome():
    return(
        '''
        Welcome to the Hawaii Climate Analysis API!<br/>
        Available Routes:<br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>
        /api/v1.0/temp/start/end
    ''')
    
# Creating a route for precipitation
@app.route("/api/v1.0/precipitation")

# Creating the precipitation function. Calculates the date one year ago from most recent date in db. Query to get date and precipitation for the previous year.
# Creating a dictionary with the date as the key and the precipitaion as the value.
def precipitation():
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip)
   
 # Creating route to stations
@app.route("/api/v1.0/stations")
# Create a query to allow the stations into db. unravel our results into a one-dimensional array. convert our unraveled results into a list
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

# Creating route to temperature
@app.route("/api/v1.0/tobs")
# Create function. Calculate the date one year ago from last date db. query the primary station for all the temperature observations from the previous year. 
# unravel the results into a one-dimensional array and convert that array into a list. jsonify temps and run it.
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

# Creating route to report on the minimum, average, and maximum temperatures. Starting and ending date
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
# Creating function. create a query to select the minimum, average, and maximum temperatures from our SQLite db.
# asterisk is used to indicate there will be multiple results for our query: minimum, average, and maximum temperatures.
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)