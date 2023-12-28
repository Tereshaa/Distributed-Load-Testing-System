import requests
import json
import time
from kafka import KafkaProducer
from kafka import KafkaConsumer
from threading import Thread

orchestrator_url = "http://localhost:8080"


producer = KafkaProducer(bootstrap_servers='localhost:9092',value_serializer=lambda v: json.dumps(v).encode('utf-8'))
consumer = KafkaConsumer('test_trigger', bootstrap_servers='localhost:9092', value_deserializer=lambda x: json.loads(x.decode('utf-8')))
config_consumer = KafkaConsumer('test_config', bootstrap_servers='localhost:9092', value_deserializer=lambda x: json.loads(x.decode('utf-8')))

def register_node():
    node_id = generate_unique_id()
    node_ip = "127.0.0.1"  

    register_message = {
        "node_id": node_id,
        "node_ip": node_ip,
        "message_type": "DRIVER_NODE_REGISTER",
    }
    send_register_message_to_kafka(register_message)

    return node_id

def send_http_request():
    start_time = time.time()
    response = requests.get("http://localhost:8081/ping")
    end_time = time.time()
    response_time = end_time - start_time
    return response_time

def consume_test_config():
    late = []
    for config_message in config_consumer:
        config = config_message.value
        if config["test_type"] == "AVALANCHE":
            for i in range(config["message_count_per_driver"]):
            	late.append(send_http_request())
        elif config["test_type"] == "TSUNAMI":
            for _ in range(config["message_count_per_driver"]):
                late.append(send_http_request())
                time.sleep(config["test_message_delay"])
        l = len(late)
        met = {
	"mean_latency": sum(late) / l,
	"median_latency": ((late[l // 2] + late[(l - 1) // 2]) / 2),
	"min_latency" : min(late),
	"max_latency" : max(late)
	}
        send_metrics_to_kafka(node_id, config["test_id"], late)

def send_metrics_to_kafka(node_id, test_id, late):
    l = len(late)
    metrics = {
        "node_id": node_id,
        "test_id": test_id,
        "report_id": generate_unique_id(),
        "metrics": {
	"mean_latency": sum(late) / l,
	"median_latency": ((late[l // 2] + late[(l - 1) // 2]) / 2),
	"min_latency" : min(late),
	"max_latency" : max(late)
	}
    }
    producer.send('metrics', value=metrics)

def main():
    global node_id
    node_id = register_node()
    print("node_id:" + node_id)
    config_consumer_thread = Thread(target=consume_test_config)
    config_consumer_thread.daemon = True
    config_consumer_thread.start()


    while True:
        istrigger= check_trigger_from_kafka(node_id)
        if istrigger:
            time.sleep(2)
            
            send_heartbeat_to_kafka(node_id)
        time.sleep(1)

def check_trigger_from_kafka(node_id):
    consumer = KafkaConsumer('test_trigger', bootstrap_servers='localhost:9092', value_deserializer=lambda x: json.loads(x.decode('utf-8')))



 
    for message in consumer:
        trigger_message = message.value
        if trigger_message.get("trigger") == "YES":
            return True  
            break
    return False  


def generate_unique_id():
    return str(int(time.time() * 1000))


def send_register_message_to_kafka(message):
    producer.send('register', value=message)



def send_heartbeat_to_kafka(node_id):
    heartbeat = {
        "node_id": node_id,
        "heartbeat": "YES",
        "timestamp": "time.time()"
    }
    producer.send('heartbeat', value=heartbeat)

if __name__ == '__main__':
    main()
