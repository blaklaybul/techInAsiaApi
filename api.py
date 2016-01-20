from flask import Flask, request, url_for, json
from flask_restful import Resource, Api
import psycopg2
from psycopg2.extras import RealDictCursor

## Create connection to PSQL

conn = psycopg2.connect("dbname = dev_techinasia user = tableau host = localhost")
print conn.encoding


app = Flask(__name__)

@app.route("/")
def api_root():
    return "Welcome to the Startup API"

@app.route("/startups")
def startups():
    cur = conn.cursor(cursor_factory = RealDictCursor)
    if 'count' in request.args:
        count = request.args["count"]
        query = "Select tiacompanyid, companyname from StartUps limit " + str(count) + ";"
        cur.execute(query)
        mike = cur.fetchall()
        print mike
        return json.dumps(mike, ensure_ascii=False)
    else:
        return "DONT WANT TO PRINT EM ALL"

if __name__ == '__main__':
    app.run()
