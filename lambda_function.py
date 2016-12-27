"""
Bhairav Mehta - Alexa Hack the Dorm Competition
Decemeber 2016

Alexa Abstractions based off a library developed by Anjishu Kumar
"""

from ask import alexa
import quizlet
import json
from random import randint

def lambda_handler(request_obj, context=None):
	return alexa.route_request(request_obj)

# Default Handler
@alexa.default
def default_handler(request):
	return alexa.create_response("Welcome! Let's start studying!")

# Launch the App
@alexa.request("LaunchRequest")
def launch_request_handler(request):
	return alexa.create_response("Welcome! Let's start studying!")

# End the session
@alexa.request("SessionEndedRequest")
def session_ended_request_handler(request):
	return alexa.create_response(message="Goodbye!", end_session=True)

# List all the sets you own and can study from
@alexa.request("ListAllSetsIntent")
def list_all_sets_request_handler(request):
	# get all of the sets
	sets = quizlet.get_all_sets_from_user()
	all_sets_titles = []
	
	title = request.slots["title"]

	set_id = None
	set_title = None

	# add each title to the list
	for set_ in sets:
		all_sets_titles.append(set_['title'])

	all_sets_string = ", ".join(all_sets_titles)
	return alexa.create_response(message="Here are the sets you can choose from: {}".format(all_sets_string))

@alexa.request("ReviewWrongAnswersIntent")
def review_all_wrong_answers_intent(request):
	if request.session['incorrect_terms'] != []:
		request.session['reviewing_wrong'] = True
		request.session['reviewing_index'] = 0
		alexa_response_str = "Sure, we can definitely review your most troublesome words. Let's start with {}".format(request.session['incorrect_terms'][0][1])
		return alexa.create_response(message=alexa_response_str)

	else:
		index = request.session['current_index']
		return alexa.create_response(message="Lucky for you, you didn't get anything wrong! Now, please define {}".format(all_terms[index]['term']))

# # Add current term to a set called "difficult"
# @alexa.request("AddToDifficultIntent")
# def add_current_word_to_difficult_set_request_handler(request):
# 	# grab the word and add it to the difficult set
# 	current_index = request.session['current_index']
# 	term_defn_to_add = request.session['all_terms'][current_index]

# 	quizlet.add_to_difficult(term_defn_to_add)

# 	return alexa.create_response(message="Got it, added to your difficult list. Let's try to define it now. Please define Please define {}".format(all_terms[current_index]['term']))


# utterance = "Alexa, quiz me on {title}"
@alexa.intent("StartStudySessionIntent")
def start_study_session_request_handler(request):
	
	# get all of the sets
	sets = quizlet.get_all_sets_from_user()
	all_sets_titles = []
	
	title = request.slots["title"]

	set_id = None
	set_title = None
	for set_ in sets:
		all_sets_titles.append(set_['title'])

		if title == set_['title']:
			set_id = set_['id']
			set_title = set_['title']

	if set_id == None:
		all_sets_string = ", ".join(all_sets_titles)
		return alexa.create_response(message="Oops! Couldn't find that set. Here are the sets you can choose from: {}".format(all_sets_string))

	else:
		request.session['study_session_set_id'] = set_id
		request.session['awaiting_set_id_confirmation'] = True
		return alexa.create_response(message="I have found your set. Can you confirm you want to study the set named {}?".format(set_title))

@alexa.intent("EndStudySessionIntent")
def end_study_session_intent_handler(request):
	total_percent_correct = int((float(request.session['correct_count']) / request.session['total_terms']) * 100)

	final_message = "I am sorry you want to leave. During this session, you got {} correct and {} incorrect out of {} \
				total terms. You got {} percent correct. Goodbye, and hopefully we speak again soon!".format(request.session['correct_count'], \
				request.session['incorrect_count'], request.session['total_terms'], total_percent_correct)
				
	return alexa.create_response(message=final_message,end_session=True)

@alexa.intent("ConfirmationIntent")
def confirmation_intent_handler(request):
	# if request.session['awaiting_set_id_confirmation'] == True:
	# 	request.session.pop('awaiting_set_id_confirmation')
		
	# store that the session has been started
	request.session['study_session_started'] = True

	terms = json.loads(quizlet.get_all_terms_given_set(request.session['study_session_set_id']))
	all_terms = []

	total_terms = 0

	for term_obj in terms:
		term_new = {}
		term_new['id'] = term_obj['id']
		term_new['definition'] = term_obj['definition']
		term_new['term'] = term_obj['term']

		total_terms += 1

		all_terms.append(term_new)

	request.session['all_terms'] = all_terms
	index = randint(0, total_terms - 1)
	request.session['used_terms'] = [False] * total_terms
	request.session['used_terms'][index] = True

	request.session['correct_count'] = 0
	request.session['incorrect_count'] = 0

	request.session['incorrect_terms'] = []

	request.session['current_index'] = index
	request.session['total_terms'] = total_terms

	return alexa.create_response(message="Great. Let's get started with the first term. Please define {}".format(all_terms[index]['term']))

	# else:
	# 	return alexa.create_response(message="Oops, try again!")

@alexa.intent('AnswerIntent')
def answer_intent_handler(request):
	if request.session['study_session_started'] and not request.session['reviewing_wrong']:
		# TODO: Make so that it does not need to match exactly
		answer = request.slots["answer"]

		index = request.session['current_index']
		total_terms = request.session['total_terms']

		if answer == request.session['all_terms'][index]['definition']:
			request.session['correct_count'] += 1

			# TODO: Check if there are any more here

			if request.session['correct_count'] + request.session['incorrect_count']  == total_terms:
				total_percent_correct = int((float(request.session['correct_count']) / total_terms) * 100)

				incorrect_terms_string = "everything, even though you don't really need it."

				if request.session['incorrect_terms'] != []:
					incorrect_terms_list = [x[1] for x in request.session['incorrect_terms']]
					incorrect_terms_string = ", ".join(incorrect_terms_list)
				

				final_message = "Good job, you got that one right! Goodbye! Thanks for finishing! You got {} correct and {} incorrect out of {} \
				total terms. You got {} percent correct, and you might want to study up on {}".format(request.session['correct_count'], \
				request.session['incorrect_count'], total_terms, total_percent_correct, incorrect_terms_string)
				
				return alexa.create_response(message=final_message,end_session=True)

			while True:
				index_try = randint(0, total_terms - 1)
				if request.session['used_terms'][index_try] == False:
					index = index_try
					request.session['used_terms'][index_try] = True
					request.session['current_index'] = index
					break

			   
			message = "Good job, you got that one right! Now, please define {}".format(request.session['all_terms'][index]['term'])

			return alexa.create_response(message=message)

		# incorrect answer
		else:
			request.session['incorrect_count'] += 1

			request.session['incorrect_terms'].append((index, request.session['all_terms'][index]['term']))

			if request.session['correct_count'] + request.session['incorrect_count']  == total_terms:
				total_percent_correct = int((float(request.session['correct_count']) / total_terms) * 100)
				incorrect_terms_list = [x[1] for x in request.session['incorrect_terms']]
				incorrect_terms_string = ", ".join(incorrect_terms_list)

				final_message = "Uh Oh, you got that one wrong! Goodbye! Thanks for finishing! You got {} correct and {} incorrect out of {} total terms. \
				You got {} percent correct, and you might want to study up on {}".format(request.session['correct_count'], \
				request.session['incorrect_count'], total_terms, total_percent_correct, incorrect_terms_string)
				
				return alexa.create_response(message=final_message, end_session=True)

			correct_def = request.session['all_terms'][index]['definition']

			while True:
				index_try = randint(0, total_terms - 1)
				if request.session['used_terms'][index_try] == False:
					index = index_try
					request.session['used_terms'][index_try] = True
					request.session['current_index'] = index
					break

			   
			message = "Uh oh, you didn't get that one right! The correct answer was {}. Now, please define {}".format(correct_def, request.session['all_terms'][index]['term'])

			return alexa.create_response(message=message)

	elif request.session['study_session_started'] and request.session['reviewing_wrong']:
		incorrect_index = request.session['reviewing_index']
		index = request.session['incorrect_terms'][incorrect_index][0]
		answer = request.slots["answer"] 

		if answer == request.session['all_terms'][index]['definition']:
			request.session['incorrect_terms'].pop(index)

			if request.session['incorrect_terms'] != []
				alexa_response_str = "Congratulations, you got that right! Now, can you define {}?".format(request.session['incorrect_terms'][incorrect_index][1])
				return alexa.create_response(message=alexa_response_str)

			else:
				alexa_response_str = "Congratulations, you finished reviewing the incorrect words from this session. Thanks for studying!"
				return alexa.create_response(message=alexa_response_str)
	
		else:
			incorrect_index += 1
			incorrect_index = incorrect_index % len(request.session['incorrect_terms'])

			alexa_response_str = "Oops, still not right. We'll come back to that. Now, can you define {}?".format(request.session['incorrect_terms'][incorrect_index][1])			


if __name__ == "__main__":	
	
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
	
