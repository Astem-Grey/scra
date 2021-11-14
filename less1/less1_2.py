import requests
import json

jobid = 'galvanized-vent-332117'

url = 'https://www.googleapis.com/youtube/v3/channels'

api_key = '***'

params = {'JOBID': jobid, 'key': api_key, 'id': 'UCS7D2OD62ADsx6j033bKCBQ'
          , 'part': 'contentDetails'}
headers = {'Content-Type': 'application/json'}

response = requests.get(url, params=params)

j_data = response.json()

with open('my_youtube_chanel.json', 'w') as f:
    json.dump(j_data, f)

# Загрузил APi своего Youtube канала, правда он у меня пустой, но зато загрузил:)
