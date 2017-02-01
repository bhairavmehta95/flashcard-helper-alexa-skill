# Flashcard Helper: An Alexa Skill

## Currently, this repo's website is under connstruction.

Flashcard Helper is an Alexa Skill that utilizes the ask-pykit library and the Alexa Skills Kit to give users an easy way to study flashcards. By connecting the skill to the Quizlet service, users can study any set of flashcards that they have uploaded or made on the website.

Flashcard Helper is a product composed of a few different pieces together:

* A Flask/Python web application hosted on Amazon Elastic Beanstalk
* An ASK-powered Alexa skill, hosted on AWS Lambda
* An Instance of an AWS RDS Amazon Databse, serving as the link between the two.

## Configuration 

Check back here later for steps on how to get the skill set up in your own environment for development and testing.

## Coding


## Things you can ask:

Flashcard Helper can do quite a few things. After visiting [http://flashcard-env.epum35ydrs.us-west-2.elasticbeanstalk.com/], signing in to Quizlet, and getting a PIN associated with an account, you can ask Flashcard Helper to help you study any of your sets, track your progress, or go over terms that you got wrong during the session. Flashcard Helper can also help you by listing all of the available sets you can study from.

Here are a few examples of things you can ask Flashcard Helper.

* Help me study history.
* What can I study?
* List my sets.
* I want to go over my incorrect answers.


Although this skill was submitted for a competition that ended on Dec. 31, 2016, it is still a work in progress. In the future
