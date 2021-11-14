import json
import requests

user = 'Astem-Grey'
url = f'https://api.github.com/users/{user}/repos'

params = {'type': 'owner'}

responce = requests.get(url, params=params)

json_data = responce.json()

with open('git_hub_repos_me.json', 'w') as f:
    json.dump(json_data, f)

# Загрузил данные о своих репозиториях, в которых владелец я. Подумал, что это подразумевалось.
# Если же нет, то я бы тут просто убрал параметр, и загрузились бы данные всех.
