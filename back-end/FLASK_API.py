from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/FetchChronologicalData', methods=['POST'])
def FetchChronologicalData():
    return jsonify({"ChronologicalData": [1,2,3,4,5]})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)