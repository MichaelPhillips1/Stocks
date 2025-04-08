from flask import Flask, jsonify, request
from assessmentFunctions import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/PriceData', methods=['GET'])
def FetchPriceData():
    data = parseDataPolygon(formPolygonQuery(request.args.get('ticker')))[1]
    return jsonify({"PriceData": data})

@app.route('/MACDData', methods=["GET"])
def FetchMACDData():
    data = calculateMACD(parseDataPolygon(formPolygonQuery(request.args.get('ticker')))[1])
    return jsonify({"MACDData": data})

@app.route('/RSIData', methods=["GET"])
def FetchRSIData():
    data = calculateRSI(parseDataPolygon(formPolygonQuery(request.args.get('ticker')))[1])
    return jsonify({"RSIData": data})

app.run(host='127.0.0.1', port=5000)