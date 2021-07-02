from twisted.internet import task, reactor
timeout = 300.0 # seconds
import json
import requests
import logging
import telebot
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
import concurrent.futures

from datetime import date, time
today = date.today()
d1 = today.strftime("%d-%m-%Y")
import time
from functools import partial

import os
from dotenv import load_dotenv

load_dotenv()

Token = os.getenv('Token')

url_data = ''

eighteen, fortyfive, no_age, all_age= [], [], [], []

def get_slot_value(res):
	if res:
		res_backup = res
		pin = res['pin_code']
		logger.info(pin)
		url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={0}&date={1}'.format(pin, d1)
		payload={}
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
		response = requests.request("GET", url, headers=headers, data=payload)
		logger.info("Response as it is from cowin: " + str(response))
		if response.status_code != 200 :
			time.sleep(120)
			logger.info("Slept due to this combination -->" + " PIN: " + str(pin))
			get_slot_value(res_backup)
		else:
			chatid_age = {}
			global eighteen 
			global fortyfive
			global no_age
			global all_age
			eighteen, fortyfive, no_age, all_age= [], [], [], []
			user = res['users']
			for dat_user in user:
				cid = dat_user['chat_id']
				age = dat_user['age_limit'] if dat_user['age_limit'] else 63 #age 63 means 18+45 i.e. for no age_limits
				chatid_age[cid] = age
				if age not in all_age:
					all_age.append(age)
				if age == 18:
					eighteen.append(cid)
				elif age == 45:
					fortyfive.append(cid)
				else:
					no_age.append(cid)
			logger.info(f'chatid_age : {chatid_age}')
			reply = json.loads(response.text)
			for ages in all_age:
				split_data_for_better_filter(reply, ages)


def split_data_for_better_filter(reply, ages):
	if reply and ages:
		func2 = partial(extract_shareble_data, ages)
		with concurrent.futures.ThreadPoolExecutor() as executorz:
			check_data1 = executorz.map(func2, reply["centers"])
			if check_data1:
				for datas in check_data1:
					filter_data_age_wise_to_send(ages, datas)

#extract and filter data that needed to be send
def extract_shareble_data(req_age, key1):
	center_detail = {"name":[], "address":[],"district_name":[], "pincode":[], "fee_type":[]}
	sessions_value ={}
	for key, value in key1.items():
		center_detail['name'] = key1['name']
		center_detail['address'] = key1['address']
		center_detail['district_name'] = key1['district_name']
		center_detail['pincode'] = key1['pincode']
		center_detail['fee_type'] = key1['fee_type']
		if key == 'sessions':
			for items in value:
				for key3 in items.keys():
					if items['available_capacity'] != 0:
						if items['min_age_limit'] == req_age:
							sessions_value['date']= items['date']
							sessions_value['available_capacity'] = items['available_capacity']
							sessions_value['min_age_limit'] = items['min_age_limit']
							sessions_value['vaccine'] = items['vaccine']
						elif req_age == 63:
							sessions_value['date']= items['date']
							sessions_value['available_capacity'] = items['available_capacity']
							sessions_value['min_age_limit'] = items['min_age_limit']
							sessions_value['vaccine'] = items['vaccine']
				if sessions_value:
					center_detail.setdefault("sessions",[]).append(sessions_value)

				sessions_value ={}
	val = list(center_detail.keys())
	if 'sessions' in val:
		return center_detail

def filter_data_age_wise_to_send(age, check_reply_data1):
	check_data1 = reply_data(check_reply_data1) #create response that can be sent
	ages = int(age)
	if check_reply_data1: #multithreading for all chatids according to age_limits
		func5 = partial(send_user, check_data1)
		if ages == 18:
			with concurrent.futures.ThreadPoolExecutor() as executor3:
				executor3.map(func5, eighteen)
		elif ages == 45:
			with concurrent.futures.ThreadPoolExecutor() as executor4:
				executor4.map(func5, fortyfive)
		else:
			with concurrent.futures.ThreadPoolExecutor() as executor5:
				executor5.map(func5, no_age)

#formattting data to send to user
def reply_data(check_data):
	send_reply_v2 = ''
	l1 = []
	if check_data:
		name = str(check_data['name'])
		addr = str(check_data['address'])
		dis = str(check_data['district_name'])
		pin = str(check_data['pincode'])
		fee = str(check_data['fee_type'])
		send_reply_v1 = "NAME: " + name + "\nADDRESS: " + addr + "\nDISTRICT: " + dis + "\nPINCODE: " + pin + "\nFEES: " + fee
		for key4 in check_data['sessions']:
			for keys1 in key4.items():
				date = str(key4['date'])
				cap = str(key4['available_capacity'])
				age_lim = str(key4['min_age_limit'])
				vac = str(key4['vaccine'])
			send_reply_v2 = 'DATE: ' + date + ',\t\tCAPACITY: ' + cap + ',\t\tAGE_LIMIT: ' + age_lim + ',\t\tVACCINE: ' + vac
			l1.append(send_reply_v2)
		return send_reply_v1, l1


#send data to user
def send_user(check_data1, c_id):
	
	if c_id and check_data1:
		url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(Token, c_id, "Congrats slots available for you, you can book your slots here https://selfregistration.cowin.gov.in/")
		response = requests.request("GET", url)
		logger.info("Response from user :   " + str(response.status_code) + "  Chat_id :  " + c_id + "  For PIN: " + c_id)
		if response.status_code == 200:
			url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(Token, c_id, check_data1[0])
			response = requests.request("GET", url)
			logger.info("Response from user :   " + str(response.status_code) + "  Chat_id :  " + c_id)
			for l in check_data1[1]:
				url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(Token, c_id, str(l))
				response = requests.request("GET", url)
				logger.info("Response from user :   " + str(response.status_code) + "  Chat_id :  " + c_id)
			url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(Token, c_id, "***************************")
			response = requests.request("POST", url)
			url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(Token, c_id, "Thank you for using VaccineMan \U0001F60A . We listened to your feedback and are excited to release this new feature where you can now filter your slots according to AGE, to know more please click --> /help")
			response = requests.request("POST", url)
		elif response.status_code == 403:
			logger.info("Chat ID has blocked our bot : " + str(c_id))
			url =  url_data + '/vaccineman/users'
			payload = json.dumps({'chat_id':str(c_id)})
			headers = {'Content-Type':'application/json'}
			response = requests.request("PUT", url, headers=headers, data=payload)
			logger.info(response.text)
			if response.status_code == 202 :
				logger.info(f"User {response.text} blocked our bot so we stoped all his PIN untill future registration")


#get pin and chatid from database
def get_user():
    url = url_data + '/vaccineman/users/tiers'
    headers = {'Content-Type':'application/json'}
    response = requests.request("GET", url, headers=headers)
    data_jsonify = json.loads(response.text)
    if response.status_code == 200:
        logger.info("List got from databse for searching:---  " + str(data_jsonify) )
        for res in data_jsonify:
            logger.info(res)
            get_slot_value(res)

#snooze time for calling the api on interval for updating user on timely basis
l = task.LoopingCall(get_user)
l.start(timeout)
reactor.run()
