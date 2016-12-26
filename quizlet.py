import keys as keys 
import requests
import json
from random import randint

BASE_URL = 'https://api.quizlet.com/2.0/'

# TODO: edit with the user from the alexa input
USERNAME = 'bhairav_mehta'


def get_all_sets_from_user(username=USERNAME):
	url = BASE_URL + 'users/' + username + '/sets'

	parameters = {
		'client_id' : keys.CLIENT_ID,
	}

	result = requests.get(url, params = parameters)

	sets = json.loads(result.text)

	all_sets = []

	########
	count = 0

	for set_ in sets:
		set_id = set_['id']
		#terms = json.loads(get_all_terms_given_set(set_id))
		new_dict = {}
		new_dict['id'] = set_id
		new_dict['title'] = set_['title']
		
		all_sets.append(new_dict)

		#run_through_set(terms, term_id)
		
	
	return all_sets

def run_through_set(terms, term_id):
	unused = [False] * len(terms)
	used_count = 0
	END_SIGNAL = False

	while used_count != len(unused) and not END_SIGNAL:
		index = randint(0, len(terms) - 1)
		if not unused[index]:
			print(terms[index]['term'])
			unused[index] = True
			used_count += 1

def get_all_terms_given_set(set):
	url = BASE_URL + 'sets/' + str(set) + '/terms'

	parameters = {
		'client_id' : keys.CLIENT_ID,
	}

	response = requests.get(url, params = parameters)	

	return response.text


if __name__ == '__main__':
	get_all_sets_from_user()

