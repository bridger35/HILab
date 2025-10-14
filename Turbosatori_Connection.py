import requests
import json
import random
#import expyriment.io.extras as ep
import time
import sys
import threading
import os

"""
Launch via 'python <file_name> <api_ip>' in cmd prompt
Can extend input with interval for accessing Turbosatori and threshold stress level for sending out to api
Turbosatori ip defualts to localhost
expyriment import and tsi functions may be commented out for testing
"""

stop_event = threading.Event()
prev_stress = 0
print("Enter \'exit\' to stop Turbosatori_Connection.py")

def monitor(api_ip,file_name,interval=3, threshold = 3,turbo_ip='localhost'):
    """
    This function loops through gathering and writing the data for Turbosatori for analysis
    :param api_ip: IP address for passing stress level to iPAL_API.py
    :param file_name: User provided file name for writing data to csv
    :param interval: value for sleep() to specify how often monitor loops
    :param threshold: min stress threshold for triggering Metahuman
    :param turbo_ip: Defualted to localhost as this is made to run on the same machine as Turbosatori
        IP address of Turbosatori machine
    :return: No return, loop until user stops or exception
    """
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
    """
    Takes values gathered from Turbosatori and proccess them into a stress value
    If the stress level exceeds threshold, pass to iPAL_API.py
    :param currentTimePoint:
    :param channels:
    :param oxy:
    :param scaleFactor:
    :param api_ip: IP address for passing stress level to iPAL_API.py
    :param threshold: min stress threshold for triggering Metahuman
    :return:
    """
    #print(f"Current Time: {currentTimePoint}, Channels: {channels}, Oxygen levels: {oxy}, Scale: {scaleFactor}")

    global prev_stress
    stress_level = str(random.randint(1,10))
    if int(stress_level) > 0 and stress_level > prev_stress:
        connect(stress_level,api_ip)
    prev_stress = stress_level

def userInput():
    """
    Runs in concurrency with Monitor(), waits for user to enter exit to gently close the program
    user inputs can be eaten by print statements(working on this)
    :return:
    """
    user=input("")
    while(user != 'exit'):
        user=input("")
    stop_event.set()
    print("Turbosatori_Connection.py waiting for thread termination")

def connect(stress_level,api_ip):
    """
    Connect to iPAL_API.py through api_ip and pass on stress_level
    :param stress_level: 1-10 value generated from Turbosatori analysis
    :param api_ip: IP address for passing stress level to iPAL_API.py
    :return:
    """
    try:

        response = requests.post(f'http://{api_ip}:5000/api/data', json={'stress_level': stress_level})

        response.raise_for_status()

        print(f"Status Code: {response.status_code}")
        print("Response Body:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


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
