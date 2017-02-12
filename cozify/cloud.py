import json, requests

cloudBase='https://cloud2.cozify.fi/ui/0.2/'

def requestlogin(email):
    payload = { 'email': email }
    response = requests.post(cloudBase + 'user/requestlogin', params=payload)
    print(response.url)
    if response.status_code == 200:
        return True
    else:
        print(response.text)
        return False
