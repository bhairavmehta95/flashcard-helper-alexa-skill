import keys as keys 
import requests
import json
from random import randint
from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine

BASE_URL = 'https://api.quizlet.com/2.0/'

# TODO: edit with the user from the alexa input
USERNAME = 'bhairav_mehta'

# gets all of the sets from the user
def get_all_sets_from_user(username=USERNAME):
	# builds url needed for quizlet api
	url = BASE_URL + 'users/' + username + '/sets'

	# imports client_id from keys.py
	parameters = {
		'client_id' : keys.CLIENT_ID,
	}

	result = requests.get(url, params = parameters)


	# loads all of the sets, returns dictionary
	sets = json.loads(result.text)

	all_sets = []

	count = 0

	for set_ in sets:
		set_id = set_['id']
		new_dict = {}
		new_dict['id'] = set_id
		new_dict['title'] = set_['title']
		
		all_sets.append(new_dict)

		
	
	return all_sets


# given a set ID, returns all of the terms associated with that set

# json.loads is done in lambda_function.py
def get_all_terms_given_set(set):
	url = BASE_URL + 'sets/' + str(set) + '/terms'

	parameters = {
		'client_id' : keys.CLIENT_ID,
	}

	response = requests.get(url, params = parameters)	

	return response.text

# given a pin code, returns a username to be used with alexa

def verify_user(pin):
	engine = create_engine(SQLALCHEMY_DATABASE_URI)
	connection = engine.connect()
	pin = str(pin)
	result = connection.execute('SELECT quizlet_username FROM flashcard_users WHERE pin_code = "{}" LIMIT 1'.format(pin))
	username = None
	for row in result:
		username = row['quizlet_username']

	connection.close()

	return username




# def add_to_difficult(term_defn_to_add, username=USERNAME):
# 	get_url = BASE_URL + 'users/' + username + '/sets'

# 	parameters = {
# 		'client_id' : keys.CLIENT_ID,
# 	}

# 	result = requests.get(url, params = parameters)

# 	sets = json.loads(result.text)

# 	difficult_set_exists = False
# 	difficult_set_id = None

# 	for s in sets:
# 		if s['title'] == "Difficult Words":
# 			difficult_set_exists = True
# 			difficult_set_id = s['id']
# 			break


# 	term = term_defn_to_add['term']
# 	term_id = term_defn_to_add['id']
# 	defn = term_defn_to_add['definition']

# 	if difficult_set_exists:
# 		post_url = "https://api.quizlet.com/2.0/sets/{}/terms".format(difficult_set_id)
		

if __name__ == '__main__':
	# sets = get_all_sets_from_user()
	# all_sets_titles = []

	# set_id = None
	# set_title = None

	# # add each title to the list
	# for set_ in sets:
	# 	all_sets_titles.append(set_['title'])

	# all_sets_string = ", ".join(all_sets_titles)
	# print("Here are the sets you can choose from: {}".format(all_sets_string))
	print verify_user(57860)
