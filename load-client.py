import requests
import json


payload = {}
typ = int(input("1: Avalanche, 2: Tsunami"))
n = int(input("message_count_per_driver"))
if typ == 1:
	payload["test_type"] = "AVALANCHE"
	payload["message_count_per_driver"] = n
elif typ == 2:
	payload["test_type"] = "TSUNAMI"
	payload["message_count_per_driver"] = n
	delay = int(input("Enter time delay"))
	payload["test_message_delay"] = delay


url = 'http://localhost:8080/startLoadTest'
response = requests.post(url, json=payload)

print(response.json())


