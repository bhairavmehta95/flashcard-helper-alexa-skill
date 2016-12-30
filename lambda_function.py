"""
Bhairav Mehta - Alexa Hack the Dorm Competition
Decemeber 2016

Alexa Abstractions based off a library developed by Anjishu Kumar
"""

from ask import alexa
import quizlet
import json
from random import randint


###### HANDLERS ######

# Lambda Handler function
def lambda_handler(request_obj, context=None):
	return alexa.route_request(request_obj)

# Default Handler
@alexa.default
def default_handler(request):
	alexa_response_str = "Welcome! Let's start studying! Please give me your pin code, found on the link listed in the Alexa app."
	return alexa.create_response(message=alexa_response_str)

###### END HANDLERS ######

###### REQUESTS ######

# Launch the App
@alexa.request("LaunchRequest")
def launch_request_handler(request):
	alexa_response_str = "Welcome! Let's start studying! Please give me your pin code, found on the link listed in the Alexa app."
	return alexa.create_response(message=alexa_response_str)

# End the session
@alexa.request("SessionEndedRequest")
def session_ended_request_handler(request):
	alexa_response_str = "Goodbye!"
	return alexa.create_response(message=alexa_response_str, end_session=True)

###### END REQUESTS ######


###### INTENTS ######

# Verifies users pin code
@alexa.intent('PinCodeIntent')
def pin_code_confirm_intent_hander(request):
	pin = request.slots['pin_code']

	# verify user by querying database using pin
	username = quizlet.verify_user(pin)

	# add username to session, welcome the user
	if username != None:
		request.session['username'] = username
		request.session['pin_code_verified'] = True
		alexa_response_str = "Welcome to Flashcard Helper {}".format(username)
		return alexa.create_response(message=alexa_response_str)

	# speak out the digits so the user can hear what the input was
	else:
		alexa_response_str = "<speak> The pin I heard was <say-as interpret-as='digits'> {} </say-as> and I couldn't find a username associated with that pin. Please try again. </speak>".format(pin)
		return alexa.create_response(message=alexa_response_str, is_ssml=True)

# List all the sets you own and can study from
@alexa.intent("ListAllSetsIntent")
def list_all_sets_intent_handler(request):
	if request.session.get('pin_code_verified') != True:
		alexa_response_str = "Please verify your pin first, using the link listed in the Alexa app."
		return alexa.create_response(message=alexa_response_str)

	# get all of the sets
	user_id = request.session['username']
	sets = quizlet.get_all_sets_from_user(user_id)
	all_sets_titles = []

	set_id = None
	set_title = None

	# add each title to the list
	for set_ in sets:
		all_sets_titles.append(set_['title'])

	# prepare response string
	all_sets_string = ", ".join(all_sets_titles)
	alexa_response_str = "Here are the sets you can choose from: {}. Let me know which one you want to work with.".format(all_sets_string)

	# return message to user
	return alexa.create_response(message=alexa_response_str)

# Review all of the wrong answers a user had during a session
@alexa.intent("ReviewWrongAnswersIntent")
def review_all_wrong_answers_intent_handler(request):
	if request.session.get('pin_code_verified') != True:
		alexa_response_str = "Please verify your pin first, using the link listed in the Alexa app."
		return alexa.create_response(message=alexa_response_str)
		
	if request.session['incorrect_terms'] != []:
		request.session['reviewing_wrong'] = True
		request.session['reviewing_index'] = 0
		alexa_response_str = "Sure, we can definitely review your most troublesome words. Let's start with {}.".format(request.session['incorrect_terms'][0][1])
		return alexa.create_response(message=alexa_response_str)

	else:
		index = request.session['current_index']
		alexa_response_str = "Lucky for you, you didn't get anything wrong! Now, please define {}.".format(request.session['all_terms'][index]['term'])
		return alexa.create_response(message=alexa_response_str)

# Starts a study session when given a set title
@alexa.intent("StartStudySessionIntent")
def start_study_session_intent_handler(request):
	if request.session.get('pin_code_verified') != True:
		alexa_response_str = "Please verify your pin first, using the link listed in the Alexa app."
		return alexa.create_response(message=alexa_response_str)

	user_id = request.session['username']

	# clears any old session data
	try:
		request.session.clear()
	except:
		pass

	# resets so user doesn't have to relog in
	request.session['username'] = user_id
	request.session['pin_code_verified'] = True
	
	# get all of the sets
	sets = quizlet.get_all_sets_from_user(user_id)
	all_sets_titles = []
	
	# grabs the title of the set from the slot
	title = request.slots["title"]

	# variables to store API call variables
	set_id = None
	set_title = None

	for set_ in sets:
		all_sets_titles.append(set_['title'])

		# found the set
		if title.lower() == str(set_['title']).lower():
			set_id = set_['id']
			set_title = set_['title']
			break

	# returns all of the options the user can choose from
	if set_id == None:
		all_sets_string = ", ".join(all_sets_titles)
		alexa_response_str = "Oops! Couldn't find that set. Here are the sets you can choose from: {}.".format(all_sets_string)
		return alexa.create_response(message=alexa_response_str)

	# found the set, looks for user confirmation
	else:
		request.session['study_session_set_id'] = set_id
		request.session['awaiting_set_id_confirmation'] = True
		alexa_response_str = "I have found your set. Can you confirm you want to study the set named {}?".format(set_title)
		return alexa.create_response(message=alexa_response_str)

# Ends the study session, gives user statistics for session
@alexa.intent("EndStudySessionIntent")
def end_study_session_intent_handler(request):
	if request.session.get('pin_code_verified') != True:
		alexa_response_str = "Please verify your pin first, using the link listed in the Alexa app."
		return alexa.create_response(message=alexa_response_str)
		
	total_percent_correct = int((float(request.session['correct_count']) / request.session['total_terms']) * 100)

	alexa_response_str = "I am sorry you want to leave. During this session, you got {} correct and {} incorrect out of {} \
				total terms. You got {} percent correct. Goodbye, and hopefully we speak again soon!".format(request.session['correct_count'], \
				request.session['incorrect_count'], request.session['total_terms'], total_percent_correct)
				
	return alexa.create_response(message=alexa_response_str,end_session=True)

# Confirms that this is the set the user wanted to study
@alexa.intent("ConfirmationIntent")
def confirmation_intent_handler(request):
	if request.session.get('pin_code_verified') != True:
		alexa_response_str = "Please verify your pin first, using the link listed in the Alexa app."
		return alexa.create_response(message=alexa_response_str)
		
	# store that the session has been started
	request.session['study_session_started'] = True
	request.session.pop('awaiting_set_id_confirmation')

	# loads all of the terms, gets them ready to be added to session
	terms = json.loads(quizlet.get_all_terms_given_set(request.session['study_session_set_id']))
	all_terms = []

	# total term counter
	total_terms = 0

	# creates a dictionary for each term, appends to a total term list
	
	''' 
	{
		'id',
		'definition',
		'term'
	}
	'''

	for t in terms:
		term_new = {}
		term_new['id'] = t['id']
		term_new['definition'] = t['definition']
		term_new['term'] = t['term']

		total_terms += 1

		all_terms.append(term_new)

	# session variables 

	request.session['total_terms'] = total_terms

	# list of all terms
	request.session['all_terms'] = all_terms
	
	# used terms boolean list
	request.session['used_terms'] = [False] * total_terms

	# incorrect term list
	request.session['incorrect_terms'] = []

	# count variables
	request.session['correct_count'] = 0
	request.session['incorrect_count'] = 0

	# reviewing wrong boolean
	request.session['reviewing_wrong'] = False

	# picks a random word to start at, marks that word used
	index = randint(0, total_terms - 1)
	request.session['used_terms'][index] = True

	# begins the session with that word
	request.session['current_index'] = index
	
	alexa_response_str = "Great. Let's get started with the first term. Please define {}".format(all_terms[index]['term'])
	return alexa.create_response(message=alexa_response_str)

# Answers to a term
'''

Currently, the utterances and speech model support answers of 1-8 words, as most flash cards definitions are
within this limit.

The answer to questions needs to be preceded by "the answer is ..." or the "the definition is ..."

'''
@alexa.intent('AnswerIntent')
def answer_intent_handler(request):
	if request.session.get('pin_code_verified') != True:
		alexa_response_str = "Please verify your pin first, using the link listed in the Alexa app."
		return alexa.create_response(message=alexa_response_str)
		
	# makes sure a study session has started and user is not reviewing his/her wrong answers
	if request.session['study_session_started'] and not request.session['reviewing_wrong']:

		# TODO: Make so that it does not need to match exactly
		answer = request.slots["answer"]

		index = request.session['current_index']
		total_terms = request.session['total_terms']

		# user got this answer correct
		if str(answer).lower() == str(request.session['all_terms'][index]['definition']).lower():

			# increment correct count for the session
			request.session['correct_count'] += 1

			# checks if this was the last term
			if request.session['correct_count'] + request.session['incorrect_count']  == total_terms:
				# percentage user got correct
				total_percent_correct = int((float(request.session['correct_count']) / total_terms) * 100)

				# default string if nothing was wrong during the entire session
				incorrect_terms_string = "everything, even though you don't really need it."

				# loads all of the incorrect terms into a string
				if request.session['incorrect_terms'] != []:
					incorrect_terms_list = [x[1] for x in request.session['incorrect_terms']]
					incorrect_terms_string = ", ".join(incorrect_terms_list)
				

				alexa_response_str = "Good job, you got that one right! Thanks for finishing! You got {} correct and {} incorrect out of {} \
				total terms. You got {} percent correct, and you might want to study up on {}. Let me know if you want to brush up on your \
				troublesome terms, or end the session for now!".format(request.session['correct_count'], \
				request.session['incorrect_count'], total_terms, total_percent_correct, incorrect_terms_string)
				
				return alexa.create_response(message=alexa_response_str)

			# not the last term, find the next term randomly
			else:	
				# loop to find the next term
				while True:
					index_try = randint(0, total_terms - 1)
					if request.session['used_terms'][index_try] == False:
						index = index_try
						request.session['used_terms'][index_try] = True
						request.session['current_index'] = index
						break

				   
				alexa_response_str = "Good job, you got that one right! Now, please define {}".format(request.session['all_terms'][index]['term'])

				return alexa.create_response(message=alexa_response_str)

		# user got this answer incorrect
		else:
			# increment incorrect count
			request.session['incorrect_count'] += 1

			# append tuple of the index and the term -- (index, term) -- to the incorrect terms list
			request.session['incorrect_terms'].append((index, request.session['all_terms'][index]['term']))

			# checks if this was the last term
			if request.session['correct_count'] + request.session['incorrect_count']  == total_terms:
				
				# percentage user got correct
				total_percent_correct = int((float(request.session['correct_count']) / total_terms) * 100)
				
				# loads all of the incorrect terms into a string
				incorrect_terms_string = ", ".join(request.session['incorrect_terms'])

				alexa_response_str = "Uh Oh, you got that one wrong! Thanks for finishing! You got {} correct and {} \
				incorrect out of {} total terms. You got {} percent correct, and you might want to study up on {}. Let me know if you want to brush up on your \
				troublesome terms, or end the session for now!" \
				.format(request.session['correct_count'], request.session['incorrect_count'], total_terms, total_percent_correct, incorrect_terms_string)
				
				return alexa.create_response(message=alexa_response_str)

			# not the last term, find the next term randomly
			else: 
				# gets the correct definition
				correct_def = request.session['all_terms'][index]['definition']

				# loop to find the next term
				while True:
					index_try = randint(0, total_terms - 1)
					if request.session['used_terms'][index_try] == False:
						index = index_try
						request.session['used_terms'][index_try] = True
						request.session['current_index'] = index
						break

				   
				alexa_response_str = "Uh oh, you didn't get that one right! The correct answer was {}. Now, please define {}."\
				.format(correct_def, request.session['all_terms'][index]['term'])

				return alexa.create_response(message=alexa_response_str)

	# study session was started, but user is reviewing their wrong answers
	elif request.session['study_session_started'] and request.session['reviewing_wrong']:

		# index of the tuple (index, term) for the word in "incorrect terms" list
		incorrect_index = request.session['reviewing_index']

		# index of that term
		index = request.session['incorrect_terms'][incorrect_index][0]

		# answer given by user
		answer = request.slots["answer"] 

		# checks if user got the answer correct
		if str(answer).lower() == str(request.session['all_terms'][index]['definition']).lower():
			
			# pops that term of the incorrect terms -- doesn't increment index 
			request.session['incorrect_terms'].pop(incorrect_index)

			# user is not done with all of the incorrect terms
			if request.session['incorrect_terms'] != []:
				# checks if the term was the last term in the list
				try:
					alexa_response_str = "Congratulations, you got that right! Now, can you define {}?".format(request.session['incorrect_terms'][incorrect_index][1])
				except:
					incorrect_index = 0
					request.session['reviewing_index'] = 0
					alexa_response_str = "Congratulations, you got that right! Now, can you define {}?".format(request.session['incorrect_terms'][incorrect_index][1])

				return alexa.create_response(message=alexa_response_str)

			# user has finished reviewing all of the incorrect terms
			else:
				alexa_response_str = "Congratulations, you finished reviewing the incorrect words from this session. Thanks for studying!"
				return alexa.create_response(message=alexa_response_str, end_session=True)
		
		# user did not get the correct answer
		else:

			# increment index circularly
			incorrect_index += 1
			incorrect_index = incorrect_index % len(request.session['incorrect_terms'])

			alexa_response_str = "Oops, still not right. We'll come back to that. Now, can you define {}?".format(request.session['incorrect_terms'][incorrect_index][1])			
			return alexa.create_response(message=alexa_response_str)

###### END INTENTS ######			


''' TODO:

Added functionality of adding to a user set called difficult, so a user can say "quiz me on the difficult terms"

'''			

# # Add current term to a set called "difficult"
# @alexa.request("AddToDifficultIntent")
# def add_current_word_to_difficult_set_request_handler(request):
# 	# grab the word and add it to the difficult set
# 	current_index = request.session['current_index']
# 	term_defn_to_add = request.session['all_terms'][current_index]

# 	quizlet.add_to_difficult(term_defn_to_add)

# 	return alexa.create_response(message="Got it, added to your difficult list. Let's try to define it now. Please define Please define {}".format(all_terms[current_index]['term']))


# Flask server for testing locally
if __name__ == "__main__":	
	print("Serving ASK")
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--serve','-s', action='store_true', default=False)
	args = parser.parse_args()
	
	if args.serve:		
		###
		# This will only be run if you try to run the server in local mode 
		##
		print('Serving ASK functionality locally.')
		import flask
		server = flask.Flask(__name__)
		@server.route('/')
		def alexa_skills_kit_requests():
			request_obj = flask.request.get_json()
			return lambda_handler(request_obj)
		server.run()
	
