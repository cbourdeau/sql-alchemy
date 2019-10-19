# 1. Import Modules
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Setup SQLite Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect database into a new model
Base = automap_base()

# Reflect tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the Database
session = Session(engine)

# 2. Create a Flask app
app = Flask(__name__)

# 3. Define static routes
@app.route("/")
def home():
    return (
        f"Welcome to the Climate API!<br/>"
        f"<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"- Dates and precipitation observations from the past year<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"- List of stations<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"- Temperature Observations from the past year<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"- Minimum, average, and max temperature for a given start day<br/>"
        f"- Provide a date in the format yyyy-mm-dd after the slash<br/>"
        f"/api/v1.0/<start><br/>"
        f"<br/>"
        f"- Minimum, average, and max temperature for a given start-end range<br/>"
        f"- Provide start and end dates in the format yyyy-mm-dd after each slash <br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # Query results to a Dictionary and return a JSON
    # Calculate the date a year ago from the last data point in the database
    a_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Design a query to retrieve the last 12 months of precipitation data 
    precipitation = session.query(Measurement.date, Measurement.prcp).\
                            filter(Measurement.date >= a_year_ago).\
                            order_by(Measurement.date.asc()).all()

    # Create a list of dicts with `date` and `prcp` as the keys and values
    prcp_totals = []
    for result in precipitation:
        row_dict = {}
        row_dict["date"] = result[0]
        row_dict["prcp"] = result[1]
        prcp_totals.append(row_dict)

    return jsonify(prcp_totals)

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset
    # Query stations
    all_stations = session.query(Station.station, Station.name).group_by(Station.station).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(all_stations))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Return a JSON list of Temperature Observations (tobs) for the previous year
    # Calculate the date a year ago from the last data point in the database
    a_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Design a query to retrieve the last 12 months of precipitation data 
    temp = session.query(Measurement.date, Measurement.tobs).\
                            filter(Measurement.date >= a_year_ago).\
                            order_by(Measurement.date.asc()).all()
    
    return jsonify(temp)

@app.route("/api/v1.0/<start>")
def start_temp(start):
    # Design a query to get the min/avg/max from a given start date
    temp_data = session.query(func.min(Measurement.tobs).\
                            label("TMIN"), func.avg(Measurement.tobs).\
                            label("TAVG"), func.max(Measurement.tobs).\
                            label("TMAX")).\
                            filter(Measurement.date >= start).all()

    # Create a dictionary from the row data and append to a list of start temp
    start_temp = []
    
    for result in temp_data:
        row_dict = {}
        row_dict["minimum temperature"] = result.TMIN
        row_dict["average temperature"] = result.TAVG
        row_dict["maximum temperature"] = result.TMAX
        start_temp.append(row_dict)

    return jsonify(start_temp)
    
        
@app.route("/api/v1.0/<start>/<end>")

def calc_temps(start, end):
    # Design a query to get the min/avg/max from a given start and end date
    temp_during_trip = session.query(func.min(Measurement.tobs).\
                            label("TMIN"), func.avg(Measurement.tobs).\
                            label("TAVG"), func.max(Measurement.tobs).\
                            label("TMAX")).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()
    
    # Create a dictionary from the row data and append to a list of trip duration
    trip_duration_info = []
     
    for result in temp_during_trip:
        row_dict = {}
        row_dict["minimum temperature"] = result.TMIN
        row_dict["average temperature"] = result.TAVG
        row_dict["maximum temperature"] = result.TMAX
        trip_duration_info.append(row_dict)

    return jsonify(trip_duration_info)


# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
