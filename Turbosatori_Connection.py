import requests
import json
import random
import expyriment.io.extras as ep
import time
import sys

#Launch via 'python <file_name> <turbosatori_ip> <api_ip>' in cmd prompt

def monitor(turbo_ip,api_ip,interval=3, threshold = 3):
    try:
        tsi = ep.TurbosatoriNetworkinterface(turbo_ip,55555)
        run=True
        while run:
            currentTimePoint = tsi.get_current_time_point()[0];
            channels = tsi.get_selected_channels()[0];
            oxy = tsi.get_data_oxy(channels[0],currentTimePoint-1)[0];
            scaleFactor = tsi.get_oxy_data_scale_factor()[0];
            analysis(currentTimePoint,channels,oxy,scaleFactor,api_ip, threshold)
            time.sleep(interval)
    except Exception as e:
        print(f"Error; {e}")

def analysis(currentTimePoint,channels,oxy,scaleFactor,api_ip, threshold):

    stress_level = str(random.randint(1,10))
    print(f"Current Time: {currentTimePoint}, Channels: {channels}, Oxygen levels: {oxy}, Scale: {scaleFactor}")
    if int(stress_level) > threshold:
        print(stress_level)
        connect(stress_level,api_ip)


def connect(stress_level,api_ip):
    try:

        response = requests.post(f'http://{api_ip}:5000/api/data', json={'stress_level': stress_level})

        response.raise_for_status()

        print(f"Status Code: {response.status_code}")
        print("Response Body:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

#Can extend input with interval for accessing Turbosatori and threshold stress level for sending out to api
monitor(sys.argv[1],sys.argv[2])
