from pymongo import MongoClient

base = MongoClient('127.0.0.1', 27017)['vkparser']
collection = base['vk']

# Тут я сделал через id, но можно и через url. Разница будет только в том, что нужно будет сначала вытащить id целевого пользователя.
# Все фаны пользователя
a = collection.find({'fans': [324685200]})
for element in a:
    print(element)
print('________')

# Все подписки пользователя
a = (collection.find_one({'user_id': 385660967}, {'fans': True, '_id': False}).get('fans'))
for i in a:
    print(collection.find_one({'user_id': i}))


