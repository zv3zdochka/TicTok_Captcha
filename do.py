import requests
from urllib.parse import urlencode
import copy

prefix = 'https://ibronevik.ru/taxi/c/tutor/api/v1/'
''' 
get_token должен возвращать { 
 'token':'...' 
 'u_hash':'...' 
} 
'''
user = get_token(get_auth_hash())


def get_task(tl_id=''):
    data = copy.deepcopy(user)
    data['tl_id'] = tl_id
    url = f'{prefix}task/select'
    encoded_data = urlencode(data)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, headers=headers, data=encoded_data)
