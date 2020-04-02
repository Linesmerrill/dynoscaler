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


@sched.scheduled_job('interval', minutes=1)
def job():
    print('Scaling ...')
    print(scale(2))


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

print("running...")
sched.start()
