import numpy as np
import requests
import base64
import json
import http.client
import socket
import concurrent.futures
import urllib.request
import time

from apscheduler.schedulers.blocking import BlockingScheduler

from config import APP, APP_URL, KEY, PROCESS

# Generate Base64 encoded API Key
message = ":" + KEY
message_bytes = message.encode('ascii')
base64_bytes = base64.b64encode(message_bytes)
base64_message = base64_bytes.decode('ascii')
# Create headers for API call
HEADERS = {
    "Accept": "application/vnd.heroku+json; version=3",
    "Authorization": base64_message
}

sched = BlockingScheduler()


def printf(format, *values):
    print(format % values)

def scale(size):
    payload = {'quantity': size}
    json_payload = json.dumps(payload)
    url = "https://api.heroku.com/apps/" + APP + "/formation/" + PROCESS
    try:
        result = requests.patch(url, headers=HEADERS, data=json_payload)
    except:
        print("test!")
        return None
    if result.status_code == 200:
        return "Success!"
    else:
        return "Failure"

# 10:00 PHX time is 17:00 UTC
# @sched.scheduled_job('cron', hour=17)
# def scale_out_to_two():
#     print('Scaling out ...')
#     print(scale(2))

# 00:00 PHX time is 07:00 UTC
# @sched.scheduled_job('cron', hour=7)
# def scale_in_to_one():
#     print('Scaling in ...')
#     print(scale(1))


def get_current_dyno_quantity():
    url = "https://api.heroku.com/apps/" + APP + "/formation"
    try:
        result = requests.get(url, headers=HEADERS)
        for formation in json.loads(result.text):
            current_quantity = formation["quantity"]
            return current_quantity
    except:
        return None


@sched.scheduled_job('interval', minutes=2)
def get_p99_response():
    print("checking p99 response")
    current_number_of_dynos = get_current_dyno_quantity()
    responseTimes = []  # in ms
    for i in range(100):
        ts = time.time()
        url = """{}?{}{}""".format(APP_URL, ts, i)
        r = requests.get(url)
        responseTimes.append(int(r.elapsed.microseconds / 1000))
    responseTimes.sort()
    p99 = float(np.round(np.percentile(responseTimes, 99), 2))
    if p99 < 1000 and current_number_of_dynos == 2:
        printf("scaling to a single dyno, p99: %s. Scale Status: %s", p99, scale(1))
    elif p99 >= 1000:
        printf("scaling up to %s dynos, p99 response time greater than or equal to 1000ms, p99: %s. Scale Status: %s",
               current_number_of_dynos+1, p99, scale(current_number_of_dynos+1))
    elif p99 < 1000 and current_number_of_dynos > 2:
        printf("scaling down to %s dynos, p99 response time is less than 1000ms, p99: %s. Scale Status: %s",
               current_number_of_dynos-1, p99, scale(current_number_of_dynos-1))
    else:
        printf("everything looks good. p99: %s and number of dynos: %s",
               p99, current_number_of_dynos)


print("""
______                   _____           _           
|  _  \                 /  ___|         | |          
| | | |_   _ _ __   ___ \ `--.  ___ __ _| | ___ _ __ 
| | | | | | | '_ \ / _ \ `--. \/ __/ _` | |/ _ \ '__|
| |/ /| |_| | | | | (_) /\__/ / (_| (_| | |  __/ |   
|___/  \__, |_| |_|\___/\____/ \___\__,_|_|\___|_|   
        __/ |                                        
       |___/                                         
""")
print("application started...")
sched.start()
