# Import
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# Database Setup - create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
Station = Base.classes.station

# Create a database session object
session = Session(engine)

# Flask Setup
app = Flask(__name__)

def calc_temps(start_date, end_date):
    """When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date."""
    
    return session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

# Define what to do when a user hits the index route
@app.route("/")
def main():
    """List all routes that are available."""
    return (
        f"Available Routes:<br/>" 
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Define what to do when a user hits the routes.

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary using `date` as the key and `prcp` as the value."""
    """Return the JSON representation of your dictionary."""
    print("Received precipitation api request.")

# Design a query to retrieve the last 12 months of precipitation data.
    last_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    max_date_string = last_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")

    first_date = max_date - dt.timedelta(365)

    precipitation_query = session.query(func.strftime("%Y-%m-%d", measurement.date), measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", measurement.date) >= first_date).all()
    
    precipitation_dict = {}
    for result in precipitation_query:
        precipitation_dict[result[0]] = result[1]

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    print("Received station api request.")

    stations_query = session.query(Station).all()

    stations_list = []
    for station in stations_query:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        stations_list.append(station_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the last year of data."""
    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    print("Received TOBS api request.")

    last_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    max_date_string = last_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")

    first_date = max_date - dt.timedelta(365)

    tob_query = session.query(measurement).\
        filter(func.strftime("%Y-%m-%d", measurement.date) >= first_date, measurement.station == 'USC00519281').all()

    tobs_list = []
    for tob in tob_query:
        tobs_dict = {}
        tobs_dict["date"] = tob.date
        tobs_dict["tobs"] = tob.tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    print("Received start date api request.")
    
    last_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    max_date = last_date_query[0][0]

    temps = calc_temps(start, max_date)

    start_list = []
    date_dict = {'start_date': start, 'end_date': max_date}
    start_list.append(date_dict)
    start_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    start_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    start_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""    
    print("Received start date and end date api request.")

    temps = calc_temps(start, end)

    #create a list
    return_list = []
    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    canonicalized_start = start.replace(" ", "").lower()
    for x in return_list:
        search_term_start = x["start"].replace(" ", "").lower()

    canonicalized_end= end.replace(" ", "").lower()
    for y in return_list:
        search_term_end = y["end"].replace(" ", "").lower()

        if search_term_start == canonicalized_start & search_term_end == canonicalized_end:
            return jsonify(return_list)
    
if __name__ == '__main__':
    app.run(debug=True)