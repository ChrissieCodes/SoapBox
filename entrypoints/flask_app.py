 
#make sure you are in the correct directory before you start the app, you silly silly girl. 
#TODO: 1. return 200 from endpoint (successfully ping the api) 2.create table to store recommendations 3. retrieve data from request 4. save request to database
from datetime import datetime
from re import T
from venv import create
from xmlrpc.client import TRANSPORT_ERROR
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import recommendations
import orm, config
import services, unitofwork

app = Flask(__name__)
# bus = bootstrap.bootstrap()
orm.start_mappers()

@app.route("/submit_recommendation", methods=["POST"])
def add_recommendation():
    content=request.get_json(silent=True)
    print(content)
    print(request)
    date = request.json["date"]
    if date is not None:
        date = datetime.fromisoformat(date).date()
    services.add_recommendation(
        request.json["matchID"],
        request.json["itemID"],
        request.json["findItem"],
        date,
        unitofwork.SqlAlchemyUnitOfWork(),
    )
    return "OK", 201

if (__name__)==("__main__"):
    app.run()