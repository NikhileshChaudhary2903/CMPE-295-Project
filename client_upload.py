import json, os 
import requests

def send_data(payload):
    url = "https://0.0.0.0:5000/"
    local_file_to_send = 'blockchain_1.py'
    files = {
        'json' : (None, json.dumps(payload), 'apllication/json'),
        'file' : (os.path.basename(local_file_to_send), open(local_file_to_send, 'rb'), 'application/octet-stream')
    }
    r = requests.post(url, files=files)

send_data({'CurrentMail': "AA", 'STRUserUUID1': "BB", 'FirstName': "ZZ",     'LastName': "ZZ",  'EE': "RR", 'JobRole': "TT"  })