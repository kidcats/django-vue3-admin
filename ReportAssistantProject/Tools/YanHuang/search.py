import json
import requests

path = '/search/v1.0/search/commands'

def commands(apirooturl, accesstoken, searchcommands):
    url = apirooturl + path
    headers = {'Authorization': 'Bearer ' + accesstoken,
               'Content-Type': 'application/json'}
    payload = searchcommands
    payload = json.dumps(payload)
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 201:
        return response.json()
    else:
        return {'Error': 'Error in commands function'}