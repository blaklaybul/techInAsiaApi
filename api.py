from flask import Flask, request
from flask_restful import Resource, Api
import psycopg2
import json

## Create connection to PSQL

conn = psycopg2.connect("dbname = dev_techinasia user = tableau host = localhost")

app = Flask(__name__)
api = Api(app)

class StartUps_Meta(Resource):
    def get(self):
        #Connect to DB
        cur = conn.cursor()
        cur.execute("Select distinct tiacompanyid from StartUps")
        return {"startup_ids": [i[0] for i in cur.fetchall()]}

class Industries(Resource):
    def get(self):
        return {"hello" : " I'm an industry!"}

api.add_resource(StartUps_Meta, "/startups")
api.add_resource(Industries, "/industries")

if __name__ == '__main__':
    app.run()
