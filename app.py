from flask import Flask, request
from pymessenger import Bot
import requests,json
import os
from utils import fetch_reply, age_categories, HELP_MSG, AGE_MSG, SEX_MSG, sex_categories, region_categories, REGION_MSG, SYM_MSG
import time

app=Flask("Dr_Bot")


#this the fb access token of your page
FB_ACCESS_TOKEN = "private"
bot = Bot(FB_ACCESS_TOKEN)


#this the the one time verification token
VERIFICATION_TOKEN = "hello"


#this is for testing by facebook
@app.route('/', methods=['GET'])
def verify():
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == VERIFICATION_TOKEN:
			return "Verification token mismatch", 403
		return request.args["hub.challenge"], 200
	return "Hello world", 200


@app.route('/',methods=['POST'])
def webhook():
	if request.method == 'POST':
		#printing of incoming data on terminal
		print(request.data)
		#conversion of byte data into json
		data=request.get_json()

		if data['object'] == "page":
			entries=data['entry']

			for entry in entries:
				messaging=entry['messaging']

				for messaging_event in messaging:

					sender_id = messaging_event['sender']['id']
					recipient_id = messaging_event['recipient']['id']

					if messaging_event.get('message'):
						#normal message handled here

						if messaging_event['message'].get('text'):
							#text message handled here

							query=messaging_event['message']['text']


							#for the debug purpose
							#bot.send_text_message(sender_id,query)
							#return "ok",200

							if messaging_event['message'].get('quick_reply'):
								#Handle quick reply here
								print("came",end="\n")
								payload = messaging_event['message']['quick_reply']['payload']
								#lets check weather the payload lie in which category
								if payload in list(zip(*age_categories))[1]:
									#store the age in mongoDB
									query = "sex input"

								#check the payload lie in sex category
								elif payload in list(zip(*sex_categories))[1]:
									#store the sex in mongoDB
									query = "region input"

								elif payload in list(zip(*region_categories))[1]:
									#store the region in mongoDB
									query = "symptom input"


							#bot.send_text_message(sender_id,"wait untill we are processsing your request")
							#return "ok",200


							#bot.send_image_url(sender_id,"https://drive.google.com/file/d/1Q_hyF7yYT4OJWaO-wzBm5LtlCM64hZpi/view?usp=sharing")
							#return "ok",200
							#send the query to the main function
							reply = fetch_reply(query, sender_id)

							#parse and send the required reply
							if reply['type'] == 'age_msg':
								bot.send_quickreply(sender_id, AGE_MSG, age_categories)

							elif reply['type'] == 'sex_msg':
								bot.send_quickreply(sender_id, SEX_MSG, sex_categories)

							elif reply['type'] == 'region_msg':
								bot.send_quickreply(sender_id, REGION_MSG, region_categories)

							elif reply['type'] == 'symptom_msg':
								bot.send_text_message(sender_id,SYM_MSG)


							elif reply['type'] == 'show_disease':
								bot.send_generic_message(sender_id,reply['data'])
								print("reply sended")
								print(reply['data'])

							elif reply['type'] == 'normal_msg':
								bot.send_text_message(sender_id,reply['data'])

							else:
								bot.send_text_message(sender_id,"mja aa rha h")				

	return "ok",200



def set_persistent_menu():
	headers = {
		'Content-Type':'application/json'
		}
	data = {
		"setting_type":"call_to_actions",
		"thread_state" : "existing_thread",
		"call_to_actions":[
			{
				"type":"postback",
				"title":"Help",
				"payload":"SHOW_HELP"
			}]
		}
	ENDPOINT = "https://graph.facebook.com/v2.8/me/thread_settings?access_token=%s"%(FB_ACCESS_TOKEN)
	r = requests.post(ENDPOINT, headers = headers, data = json.dumps(data))
	print(r.content)


set_persistent_menu()

if __name__=="__main__":
	app.run(port=8002,use_reloader=True)


