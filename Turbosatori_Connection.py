import requests
import json
import random
#import expyriment.io.extras as ep
import time
import sys
import threading
import os

#Launch via 'python <file_name> <turbosatori_ip> <api_ip>' in cmd prompt

stop_event = threading.Event()
print("Enter \'exit\' to stop Turbosatori_Connection.py")
def monitor(api_ip,file_name,interval=3, threshold = 3,turbo_ip='localhost'):
    try:
        if not os.path.exists('turbosatori_output'):
            os.makedirs('turbosatori_output')
        if os.path.exists('turbosatori_output/'+file_name+'.csv'):
            file_name+=str(int(time.time()))
        f = open('turbosatori_output/'+file_name+'.csv', "w")
        f.write("currentTimePoint,channels,oxy,scaleFactor\n")

        #tsi = ep.TurbosatoriNetworkInterface(turbo_ip,55555)
        while not stop_event.is_set():
            data=[]
            currentTimePoint = 1#tsi.get_current_time_point()[0]
            data.append(currentTimePoint)
            channels = 1#tsi.get_selected_channels()[0]
            data.append(channels)
            oxy = 1#tsi.get_data_oxy(channels[0],currentTimePoint-1)[0]
            data.append(oxy)
            scaleFactor = 1#tsi.get_oxy_data_scale_factor()[0]
            data.append(scaleFactor)
            Line = ""
            for item in data:
                if not Line:
                    Line+=str(item)
                else:
                    Line+=','
                    Line+=str(item)
            f.write(f"{Line}\n")
            analysis(currentTimePoint,channels,oxy,scaleFactor,api_ip, threshold)
            time.sleep(interval)

    except Exception as e:
        print(f"Error; {e}")

def analysis(currentTimePoint,channels,oxy,scaleFactor,api_ip, threshold):

    stress_level = str(random.randint(1,10))
    print(f"Current Time: {currentTimePoint}, Channels: {channels}, Oxygen levels: {oxy}, Scale: {scaleFactor}")
    if int(stress_level) > 0:
        print(stress_level)
        connect(stress_level,api_ip)

def userInput():
    user=input("")
    while(user != 'exit'):
        user=input("")
    stop_event.set()
    print("Turbosatori_Connection.py waiting for thread termination")

def connect(stress_level,api_ip):
    try:

        response = requests.post(f'http://{api_ip}:5000/api/data', json={'stress_level': stress_level})

        response.raise_for_status()

        print(f"Status Code: {response.status_code}")
        print("Response Body:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

#Can extend input with interval for accessing Turbosatori and threshold stress level for sending out to api
#Turbosatori ip defualts to localhost
#Intialize threads
threads = []
#Intialize monitor loop
thread = threading.Thread(target=monitor, args=(sys.argv[1],sys.argv[2]))
threads.append(thread)
thread.start()

#Intiliaze User input loop
thread = threading.Thread(target=userInput)
threads.append(thread)
thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

print("All threads have finished.")
