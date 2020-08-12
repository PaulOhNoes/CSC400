from django.test import TestCase

# Create your tests here.
import requests
import pprint
import os

text_query = 'food bank in 06850'.replace(" ", "+")
# fields: business_status, formatted_address, geometry[location][lat], geometry[location][lng], name,
# opening_hours[open_now], user_ratings_total

list_results = []
# dic = {'name': None, 'formatted_address': None}

api_key = os.getenv('api_key')
http_link = 'https://maps.googleapis.com/maps/api/place/textsearch/output?parameters'
example = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&key={}'.format(text_query, api_key)


response = requests.get(example)
data = response.json()

for x in range(len(data['results'])):
    list_results.append({'name': data['results'][x]['name'],
                         'formatted_address': data['results'][x]['formatted_address'],
                         'business_status': data['results'][x]['business_status'],
                         'user_ratings_total': data['results'][x]['user_ratings_total'],})
    try:
        list_results[x]['open'] = data['results'][x]['opening_hours']['open_now']
    except:
        list_results[x]['open'] = None

pprint.pprint(list_results)
