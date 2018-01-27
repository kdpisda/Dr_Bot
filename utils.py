import apiai
import json
import requests
from pymongo import MongoClient


#all images we are gonna use
IMG0 = ""
IMG1 = ""
IMG2 = ""
IMG3 = ""
IMG4 = ""
IMG5 = ""
IMG6 = ""
IMG7 = ""
IMG8 = ""
IMG9 = ""



# api.ai client 
APIAI_ACCESS_TOKEN = "private"
ai = apiai.ApiAI(APIAI_ACCESS_TOKEN)

#pymongo client for the database
MONGODB_URI = "private" #every mongo db has a Universal resource identify URI
client = MongoClient(MONGODB_URI)
db = client.get_database("bot")
symp=db.symptom_store

#medico api endpoint
hack36medico_endpoint = "private"

#medicine api endpoint
hack36medicine_endpoint = "private"

# Available age categories
age_categories = [('newborn', '1'),('infant', '2'),('younger child','3'),('older child','10'),('adolescent','4'),('young adult','7'),('adult below 40','5'),('adult below 50','8'),('adult below 65','9'),('senior','6')]

# Available sex categories -30
sex_categories = [('male','31'),('female','32')]

# Available region categories -10
region_categories = [('North America','22'),('South America','25'),('Central America','23'),('Africa','13'),('East Asia','19'),('South Asia','20'),('Southeast Asia','18'),('Australasia','26'),('Eastern europe','12'),('Middle East','27')]

SYM_MSG = """
That's it, now write 'symptoms' without quotes and
then write your symptoms separated by comma(,)
^_^
"""

#a help message
HELP_MSG = """
Hey! I am your Dr. Bot.
I can check your symptoms from over 6000 symptoms.
Check me out. just type
'check my symptoms' without quotes
Find and buy medicines. just type
'medicines' without quotes followed by medicine name
:)
"""

#message along with check my symptoms
AGE_MSG = """
Please select your age from given below 
:)
"""

#message along with check my symptoms
SEX_MSG = """
Cool, go on and select your gender 
:P
"""

#message along with check my symptoms
REGION_MSG = """
Awesome, now select your region from given below.
Region is specified since some diseases are region specified
:-D
"""

#apiai response added
def apiai_response(query, session_id):
	"""
	function to fetch api.ai response
	"""
	request = ai.text_request()
	request.lang='en'
	request.session_id=session_id
	request.query = query
	response = request.getresponse()
	return json.loads(response.read().decode('utf8'))


#function to deal with hack36medico
def medico_api(params):
	r = requests.get(hack36medico_endpoint,params=params)
	return r.json()


#function to deal with hack36medicine
def medicine_api(params):
	r=requests.get(hack36medicine_endpoint,params=params)
	return r.json()


def fetch_reply(query, session_id):
	"""
	main function to fetch the reply for chatbot
	and return a reply dict with reply 'type' and 'data'
	"""

	reply={}
	data={}
	data['session_id']=str(session_id)
	# initiate the symptoms process
	if query == "check my symptoms":

		#then send it a quick reply
		reply['type'] = 'age_msg'
		reply['data'] = 'none'

	elif query == "sex input":

		#then send the quick reply of sex
		reply['type'] = 'sex_msg'
		reply['data'] = 'none'

	elif query == "region input":

		#then send the quick reply of region
		reply['type'] = 'region_msg'
		reply['data'] = 'none'

	elif query == "symptom input":

		#then send the postback to take the 
		reply['type'] = 'symptom_msg'
		reply['data'] = 'none'

	else:
		#handle /symptoms here
		arr = query.split(' ',1)
		if arr[0] == "symptoms":
			reply['type'] = 'show_disease_processing'
			print(arr[1])
			# now retrive the age,sex and region from mongoDB
			#retrive age ,sex, region, from mongoDB
			#reply['data'] = "please wait untill we process your request ;)"
			#return reply

			#check weather the flag is 1 or 0
			#if 0 then process the query else return we are processing your query
			temp=symp.find_one({'session_id':str(session_id)})

			if temp['flag'] == '1':
				reply['type'] = 'show_disease_processed'
				reply['data'] = ''
				return reply

			params={
			'age':temp['age'],
			'sex':temp['sex'],
			'region':temp['region'],
			'symptoms':arr[1]
			}



			final_diseases=medico_api(params)

			final_list = []

			count = 0
			for article in final_diseases:
				if count > 9:
					break
				count += 1
				element = {}
				element['title'] = article['name']
				element['item_url'] = article['link']
				if article['flag'] == 0:
					element['subtitle'] = "Not serious"
				elif article['flag'] == 1:
					element['subtitle'] = "serious diseases"
				element['image_url'] = "https://drive.google.com/file/d/1VF0vdGeDTbGuaCB-2uKX3mbzqvSPZXy_/view?usp=sharing"#article['img']
				#element['default_action'] = {"webview_height_ratio":"tall"}
				element['buttons'] = [{
					"type":"web_url",
					"title":"Read more",
					"url":article['link']
				}]
				final_list.append(element)

			reply['data'] = final_list
			print("reply generated")
			data['flag'] = '1'
			symp.update_one({'session_id':str(session_id)},{"$set":data})
			print("data updated with flag one")


		#for the medicine
		elif arr[0] == "medicines":
			reply['type'] = 'show_disease_processing'
			print(arr[1])
			temp=symp.find_one({'session_id':str(session_id)})
			print("came back from mongoDB")
			if temp['flag2'] == '1':
				reply['type'] = 'show_disease_processed'
				reply['data'] = ''
				return reply
			print("going to 1mg")
			params={
			'medicine_name':arr[1]
			}



			final_diseases=medicine_api(params)
			print("came from 1mg")
			final_list = []

			##count = 0
			for article in final_diseases:
				#if count > 9:
					#break
				#count += 1
				element = {}
				element['title'] = article['name']
				element['item_url'] = article['link']
				element['subtitle'] = "price : Rs" + article['price'] +'\n' + 'No. of Tablets : ' + article['tablets']
				element['image_url'] = "https://drive.google.com/file/d/1VF0vdGeDTbGuaCB-2uKX3mbzqvSPZXy_/view?usp=sharing"#article['img']
				#element['default_action'] = {"webview_height_ratio":"tall"}
				element['buttons'] = [{
					"type":"web_url",
					"title":"Buy Now",
					"url":article['link']
				}]
				final_list.append(element)

			reply['data'] = final_list
			print("reply generated")
			data['flag2'] = '1'
			symp.update_one({'session_id':str(session_id)},{"$set":data})
			print("data updated with flag2 one")
			print(final_list)

			

		else:
			#pass the response in the small talk
			response = apiai_response(query, session_id)

			#if the answer is trained
			if response['result']['action'].startswith('smalltalk'):
				reply['type'] = 'smalltalk'
				reply['data'] = response['result']['fulfillment']['speech']

			#if the answer is not trained
			else:
				reply['type'] = 'none'
				reply['data'] = [{"type":"postback",
								  "payload": "SHOW_HELP",
								  "title":"Click here for help!"}]



	return reply

