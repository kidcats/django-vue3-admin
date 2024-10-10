import requests

path = '/fsum/oauth2.0/token'

def getToken(apiurl, username, password):
    apiurl = apiurl + path
    payload = {
        'username': username,
        'password': password,
        "grant_type": "password",
        "client_id": "fs-oauth-client"
    }
    response = requests.post(apiurl, data=payload, headers={'Content-Type': "application/x-www-form-urlencoded"}, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        return None