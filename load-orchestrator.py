from flask import Flask, request, jsonify
import json
import time
from kafka import KafkaProducer
from kafka import KafkaConsumer
import requests

app = Flask(__name__)


producer = KafkaProducer(bootstrap_servers='localhost:9092',value_serializer=lambda v: json.dumps(v).encode('utf-8'))
consumer = KafkaConsumer('metrics', bootstrap_servers='localhost:9092', value_deserializer=lambda x: json.loads(x.decode('utf-8')))
heartbeats = KafkaConsumer('heartbeat', bootstrap_servers='localhost:9092', value_deserializer=lambda x: json.loads(x.decode('utf-8')))


metrics={}

last_heartbeat_timestamps = {}

# Initializes two global dictionaries: metrics to store
# metrics received from the 'metrics' Kafka topic, and 
# last_heartbeat_timestamps to store the timestamps of 
# the last received heartbeats from the 'heartbeat' 
# Kafka topic.

def check_node_status(): #heartbeat checking function
    while True:
        current_time = time.time()
        for message in heartbeats:
            heartbeat = message.value
            node_id = heartbeat.get("node_id")
            timestamp = heartbeat.get("timestamp")
        
            last_heartbeat_timestamps[node_id] = timestamp
            
        check_missing_heartbeats(current_time)
        time.sleep(5)

def check_missing_heartbeats(current_time):
    missing_nodes = []
    heartbeat_timeout = 10  #threshold

    for node_id, last_timestamp in last_heartbeat_timestamps.items():
        if current_time - last_timestamp > heartbeat_timeout:
            missing_nodes.append(node_id)

    if missing_nodes:
        print("Missing Heartbeats - Dead Nodes:")
        for dead_node in missing_nodes:
            print(f"Node ID: {dead_node} is dead")


def process_metrics():
    for message in consumer:
        metrics[message.value['test_id']]=message.value['metrics']
        print(metrics)
        try:
            response = requests.post('http://127.0.0.1:8081/test', json=metrics)
            if response.status_code == 200:
                continue
            else:
                print(f"Failed to forward metrics. Status code: {response.status_code}")

        except Exception as e:
            print(f"An error occurred while forwarding metrics: {str(e)}")
    


driver_nodes = {}

@app.route('/startLoadTest', methods=['POST'])
def start_load_test():
    data = request.json
    test_id = generate_unique_id()

    config = {
        "test_id": test_id,
        "test_type": data.get("test_type", "AVALANCHE"),
        "test_message_delay": data.get("test_message_delay", 0),
        "message_count_per_driver": data.get("message_count_per_driver",1),
    }
    send_test_config_to_kafka(config)

    trigger = {
        "test_id": test_id,
        "trigger": "YES",
    }
    send_test_trigger_to_kafka(trigger)

    return jsonify({"message": f"Load test started with Test ID: {test_id}"}), 200

def generate_unique_id():
    return str(int(time.time() * 1000))

def send_test_config_to_kafka(config):
    producer.send('test_config', value=config)
    

def send_test_trigger_to_kafka(trigger):
    producer.send('test_trigger', value=trigger)
   

if __name__ == '__main__':
    from threading import Thread
    consumer_thread = Thread(target=process_metrics)
    consumer_thread.daemon = True
    consumer_thread.start()
    heartbeat_thread = Thread(target= check_node_status)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()
    app.run(host='127.0.0.1', port=8080)