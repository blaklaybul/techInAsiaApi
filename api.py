from flask import Flask, request, url_for, json, render_template, send_from_directory
import psycopg2
from psycopg2.extras import RealDictCursor

import graph as gpy

## Create connection to PSQL

conn = psycopg2.connect("dbname = dev_techinasia user = tableau host = localhost")

app = Flask(__name__)

#need to enable CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route("/")
def api_root():
    return send_from_directory("static","index.html")

@app.route("/startups")
def startups():
    cur = conn.cursor(cursor_factory = RealDictCursor)
    if 'count' in request.args:
        count = request.args["count"]
        query = "SELECT tiacompanyid, companyname FROM StartUps LIMIT " + str(count) + ";"
        cur.execute(query)
        mike = cur.fetchall()
        return json.dumps(mike, ensure_ascii=False)
    else:
        return "DONT WANT TO PRINT EM ALL"

@app.route("/countries")
def countries():
    cur = conn.cursor(cursor_factory = RealDictCursor)
    query = """
        SELECT DISTINCT
            COUNTRY
        FROM (
            SELECT
                COUNTRY AS COUNTRY
            FROM STARTUPS
            UNION ALL
            SELECT
                INVESTORLOCATION AS COUNTRY
            FROM INVESTORS
            ) as place;
        """
    cur.execute(query)
    mike = cur.fetchall()
    response = {"countries": [country["country"] for country in mike]}
    return json.dumps(response, ensure_ascii=False)

@app.route("/industries")
def getIndustries():
    cur = conn.cursor(cursor_factory = RealDictCursor)
    if "top" in request.args:
        top = request.args["top"]
        query = "SELECT industryname FROM industries GROUP BY industryname ORDER BY RANDOM() LIMIT " + str(top) + ";"
        cur.execute(query)
        mike = cur.fetchall()
        response = {"industries": [industry["industryname"] for industry in mike]}
        return json.dumps(response, ensure_ascii=False)

@app.route("/industryGraph/<string:industry>")
def industryGraph(industry):
    print industry
    if 'subgraphs' in request.args:
        subgraphs = request.args["subgraphs"]
        subgraphs = int(subgraphs)
        industry = industry.replace("_"," ")
        response = gpy.main(industry,conn, subgraphs)
        return json.dumps(response, ensure_ascii=False)
    else:
        return "PLEASE ADD AN INDUSTRY ARGUMENT"



if __name__ == '__main__':
    app.run()
