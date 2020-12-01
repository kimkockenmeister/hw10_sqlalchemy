
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

#Save table references
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create session
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def main():
    """List all routes that are available."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a query results in a dictionary """

    finaldate = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_string = finaldate[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")
    begin_date = max_date - dt.timedelta(365)
    precipitation_list = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).all()

    results = {}
    for result in precipitation_list:
        results[result[0]] = result[1]

    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all station names"""
    #list
    stations = session.query(Station).all()

    #create a list of dictionaries
    stations_list = []
    for station in stations:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the previous year"""
    # find temperature data for the last year
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    #find the last date in the database
    max_date_string = final_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")

    # beginning of search query
    begin_date = max_date - dt.timedelta(365)

    #get temperature measurements for last year
    results = session.query(Measurement).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).all()

    # list of dictionaries 
    tobs_list = []
    for result in results:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
   #"""Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
	starting_date = dt.datetime.strptime(start,"%Y-%m-%d")
	# Query Min, Max, and Avg based on date
	summary_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
	filter(Measurement.date >= starting_date).all()
	session.close() 
	
	summary_list = list(np.ravel(summary_stats))

	
	return jsonify(summary_list)

@app.route("/api/v1.0/<start>/<end>")
def duration(start,end):

	Start_Date = dt.datetime.strptime(start,"%Y-%m-%d")
	End_Date = dt.datetime.strptime(end,"%Y-%m-%d")

	summary_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
	filter(Measurement.date.between(Start_Date,End_Date)).all()

	session.close()    
	
	summary = list(np.ravel(summary_stats))

	return jsonify(summary)

if __name__ == "__main__":
	app.run(debug=True)