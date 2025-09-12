import requests
import json
import random


try:
    random = str(random.randint(1,10))
    response = requests.post('http://localhost:5000/api/data', json={'stress_level': random})
    
    response.raise_for_status() 

    print(f"Status Code: {response.status_code}")
    print("Response Body:", response.text)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
