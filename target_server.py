from flask import Flask, jsonify, request
import time
import random
import json


app = Flask(__name__)

request_count = 0
response_count = 0

stored_data = {}  #store data received through the /test endpoint's POST requests. 


@app.route('/test', methods=['GET']) #to retrieve stored data
def get_data():
    if request.method == 'GET':
        return jsonify(stored_data), 200

@app.route('/test', methods=['POST'])#to update stored data
def post_data():
    if request.method == 'POST':
        try:
            data = request.json  
            stored_data.update(data)  
            return jsonify({'message': 'Data received and stored successfully'}), 200
        except Exception as e:
            return jsonify({'error': 'Invalid JSON data', 'details': str(e)}), 400


@app.route('/ping', methods=['POST','GET'])
def ping_endpoint():
    global request_count
    request_count += 1

    time.sleep(random.uniform(0.1, 0.5)) #imulates a delay between 0.1 and 0.5 seconds before responding.

    global response_count
    response_count += 1

    return "Response from test endpoint", 200

@app.route('/metrics', methods=['POST','GET'])
def metrics_endpoint():
    return jsonify({
        "total_requests": request_count,
        "total_responses": response_count
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081)
