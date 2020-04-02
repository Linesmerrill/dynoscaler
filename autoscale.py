import requests
import base64
import json

from apscheduler.schedulers.blocking import BlockingScheduler

from config import APP, KEY, PROCESS

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
@sched.scheduled_job('cron', hour=17)
def scale_out_to_two():
    print('Scaling out ...')
    print(scale(2))

# 00:00 PHX time is 07:00 UTC
@sched.scheduled_job('cron', hour=7)
def scale_in_to_one():
    print('Scaling in ...')
    print(scale(1))

def get_current_dyno_quantity():
    url = "https://api.heroku.com/apps/" + APP + "/formation"
    try:
        result = requests.get(url, headers=HEADERS)
        for formation in json.loads(result.text):
            current_quantity = formation["quantity"]
            return current_quantity
    except:
        return None

@sched.scheduled_job('interval', minutes=3)
def fail_safe():
    print("pinging ...")
    r = requests.get('https://APPNAME.herokuapp.com/')
    current_number_of_dynos = get_current_dyno_quantity()
    if r.status_code < 200 or r.status_code > 299:
        if current_number_of_dynos < 3:
            print('FAIL SAFE: Bad status code: Scaling out ...')
            print(scale(2))
    if r.elapsed.microseconds / 1000 > 5000:
        if current_number_of_dynos < 3:
            print('FAIL SAFE: Response greater than 5 seconds: Scaling out ...')
            print(scale(2))

print("started running...")
sched.start()
