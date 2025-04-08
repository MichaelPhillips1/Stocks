from flask import Flask, jsonify, request
import requests.adapters
from assessmentFunctions import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/PriceData', methods=['GET'])
def FetchChronologicalData():
    data = parseDataPolygon(formPolygonQuery(request.args.get('ticker')))[1]
    return jsonify({"PriceData": data})

app.run(host='127.0.0.1', port=5000)