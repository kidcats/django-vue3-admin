import base64
import json
import requests

path = '/inuit/v1.0/auth/login'

def login(apiurl, username, password):
    apiurl = apiurl + path
    password = base64.b64encode(password.encode('utf-8')).decode('utf-8')
    payload = {
        'username': username,
        'password': password
    }
    payload = json.dumps(payload)
    response = requests.post(apiurl, data=payload, headers={'Content-Type': 'application/json'})
    if response.status_code == 201:
        return response.json()
    else:
        return None



