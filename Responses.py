from datetime import datetime
# from Constants import url_data, logger, API_KEY
import json
import requests

API_KEY = ''
url_data = ''

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def commad_list():
	help_data = f"1. This is a slot finder bot, that find slots for your registered PIN. \n\
	2. You can register for as many PINs you want. \n\
	3. We can filter your slots for your desired age group too. \n\
	4. Please send your PIN only for all age_limits or PIN and age_limit(18/45) for slot details in below format:- \n110002 18 \n110002 45 \n11002  \ni.e. PIN age_limit \n\
	5. You can stop all incoming notifications by sending /stop or stop \n\
	6. You can stop notification for single PIN by sending stop PIN i.e. stop 110002 \n\
	7. For now we can only find slots for you and if found we provide COWIN site link please go there and book your slots. We can\'t book it for you"
	return help_data

def start_response():
    response = f"VaccineMan is at your service...\n Please send your PIN only for all age_limits or PIN and age_limit(18/45) for slot details in below format:- \n110002 18 \n110002 45 \n11002  \ni.e. PIN age_limit"
    return response

def stop_notification(chatid, messages=None):
	id = chatid
	if messages:
		res = messages.split(' ')
		if len(res) == 2 and len(res[1]) == 6 and all(c.isdigit() for c in res[1]) is True:
			pin = res[1]
			logger.info(f"Chat ID: {str(id)} asked to stop for PIN: {str(pin)}" )
			url =  url_data + '/vaccineman/users'
			payload = json.dumps({'chat_id':str(id), 'pin_code':str(pin)})
			headers = {'Content-Type':'application/json'}
			response = requests.request("PUT", url, headers=headers, data=payload)
			logger.info(response.text)
			if response.status_code == 202 :
				logger.info("User stopped service : " + str(response.text))
				return f"All your notifications for PIN: {pin} are terminated now, feel free to register with your PIN, if you need our service again."
		
		else:
			url =  url_data + '/vaccineman/users'
			payload = json.dumps({'chat_id':str(id)})
			headers = {'Content-Type':'application/json'}
			response = requests.request("PUT", url, headers=headers, data=payload)
			logger.info(f'response:  {response}')
			return f"All your notifications are terminated now, feel free to register with your PIN, if you need our service again"

	else:
		url =  url_data + '/vaccineman/users'
		payload = json.dumps({'chat_id':str(id)})
		headers = {'Content-Type':'application/json'}
		response = requests.request("PUT", url, headers=headers, data=payload)
		logger.info(f'response:  {response}')
		return f"All your notifications are terminated now, feel free to register with your PIN, if you need our service again"

#extract data from the reponse of API_SETU
def extract_shareble_data(key1, total_centers_for_PIN, req_age=None):
	center_detail = {"name":[], "address":[],"district_name":[], "pincode":[], "fee_type":[]}
	sessions_value ={}
	count_val = total_centers_for_PIN
	i = 0
	for key, value in key1.items():
		i +=1
		center_detail['name'] = key1['name']
		center_detail['address'] = key1['address']
		center_detail['district_name'] = key1['district_name']
		center_detail['pincode'] = key1['pincode']
		center_detail['fee_type'] = key1['fee_type']
		if key == 'sessions':
			for items in value:
				for key3 in items.keys():
					if items['available_capacity'] != 0:
						if req_age and str(items['min_age_limit']) == req_age:
							sessions_value['date']= items['date']
							sessions_value['available_capacity'] = items['available_capacity']
							sessions_value['min_age_limit'] = items['min_age_limit']
							sessions_value['vaccine'] = items['vaccine']
							sessions_value['dose1'] = items['available_capacity_dose1']
							sessions_value['dose2'] = items['available_capacity_dose2']
						elif req_age == 'no_age_limit':
							sessions_value['date']= items['date']
							sessions_value['available_capacity'] = items['available_capacity']
							sessions_value['min_age_limit'] = items['min_age_limit']
							sessions_value['vaccine'] = items['vaccine']
							sessions_value['dose1'] = items['available_capacity_dose1']
							sessions_value['dose2'] = items['available_capacity_dose2']
				if sessions_value:
					center_detail.setdefault("sessions",[]).append(sessions_value)

				sessions_value ={}
	val = list(center_detail.keys())
	if 'sessions' in val:
		logger.info(center_detail)
		return center_detail
	if i == count_val:
		return None

#create reply data needed to be send to user
def reply_data(key1, total_centers_for_PIN, req_age=None):
	check_data = extract_shareble_data(key1, total_centers_for_PIN, req_age)
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
				cap1 = str(key4['dose1'])
				cap2 = str(key4['dose2'])
				age_lim = str(key4['min_age_limit'])
				vac = str(key4['vaccine'])
			send_reply_v2 = 'DATE: ' + date + ',\t\tDose1_Capacity: ' + cap1 + ',\t\tDose2_Capacity: ' + cap2 + ',\t\tAGE_LIMIT: ' + age_lim + ',\t\tVACCINE: ' + vac
			l1.append(send_reply_v2)
		return send_reply_v1, l1
	elif check_data is None:
		return None


def mrA_api(id, pin, age=None):
	if id and pin:
		url = url_data + '/vaccineman/users'
		payload = json.dumps({'chat_id':str(id), 'pin_code':pin, 'age_limit':age})
		headers = {'Content-Type':'application/json'}
		response = requests.request("POST", url, headers=headers, data=payload)
		logger.info("Response from mrA :  " + str(response.text))
		return response


def check_pin_and_age_first_level(message, chatid):
	req = message.split()
	age = ['18', '45']
	if len(req[0]) == 6 and all(c.isdigit() for c in req[0]) is True :
		if len(req) == 2 :
			if str(req[1]) in age:
				check_pin = mrA_api(chatid, req[0], str(req[1]))
				if check_pin.status_code == 201 :
					return req[0], str(req[1])
				else:
					return 403
			else:
				return 'wrong age'
		else:
			check_pin = mrA_api(chatid, req[0])
			if check_pin.status_code == 201 :
				return req[0], 'no_age_limit'
			else:
				return 403
	else:
		return None


def hello(messages, chatid, d1):
	request = messages.split()
	logger.info("Chat ID: " + str(chatid))
	logger.info("mssg send by above chat ID:" + str(messages))

	if request[0].lower() in ['hi', 'hello', 'start', 'yo', 'hola']:
		msg_start = start_response()
		bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
		response = requests.request("GET", bot_url)

	elif len(request[0]) == 6 :
		msg_start = f"PIN looks okay let me verify it...."
		bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
		response = requests.request("GET", bot_url)
		result_check_pin_and_age = check_pin_and_age_first_level(messages, chatid)

		if result_check_pin_and_age is None:
			msg_start = f"Please send your data in correct format mentioned above ..."
			bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
			response = requests.request("GET", bot_url)
			logger.info(f"Asked {chatid} to send correct data ")

		elif result_check_pin_and_age == 403:
			msg_start = f"Check you PIN please, it's invalid"
			bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
			response = requests.request("GET", bot_url)
			logger.info(f"{chatid} has send wrong PIN ")
		
		elif result_check_pin_and_age == 'wrong age':
			msg_start = f"Please provide PIN with age_limit as 18 or 45 or don't pass age_limit if you want to register for all age_limits"
			bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
			response = requests.request("GET", bot_url)
			logger.info(f"{chatid} has send wrong PIN ")

		else:
			logger.info("===========================")
			req = result_check_pin_and_age[0]
			req_age = result_check_pin_and_age[1]
			logger.info(f"CHAT_ID : {chatid}")
			logger.info(f"PIN : {req}")
			logger.info(f"DATE ----------- : {d1}")
			url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={0}&date={1}'.format(req, d1)
			payload={}
			headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

			response = requests.request("GET", url, headers=headers, data=payload)
			reply = json.loads(response.text)
			if reply == {'centers': []}:
				msg_start = f"No slots found now for your PIN {req} for age_limit {req_age}, we'll keep looking and notify you ASAP. Till then be safe!"
				bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
				response = requests.request("GET", bot_url)

			else:
				congrats_flag = 0 	#this flag enables to send congrats to user only once if slot available
				total_centers_for_PIN = 0	#total number of centers available for this pin
				count_total_centers_for_PIN = 0 	#this flag to match above flag count to check if we have check all centers
				ommit_respose_with_zero_available_capacity_flag = 0 	#if this flag remain 0 then no available capacity was there but we got reponse from the api_setu
				total_centers_for_PIN = len(reply["centers"])
				logger.info(str(chatid) + "  ***************   " + str(total_centers_for_PIN))

				for key1 in reply["centers"]:
					check_data1 = reply_data(key1, total_centers_for_PIN, req_age)
					logger.info(check_data1)
					count_total_centers_for_PIN +=1

					if check_data1:
						ommit_respose_with_zero_available_capacity_flag = 1

						if congrats_flag == 0:
							msg_start = f"Congrats slots available for you, you can book your slots here https://selfregistration.cowin.gov.in/"
							bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
							response = requests.request("GET", bot_url)
							
							congrats_flag = 1
						msg_start = f"{check_data1[0]}"
						bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
						response = requests.request("GET", bot_url)
						logger.info("Response from user :   " + str(check_data1[0]))

						for l in check_data1[1]:
							msg_start = f"{l}"
							bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
							response = requests.request("GET", bot_url)
							logger.info("Response from user :   " + str(l))

						msg_start = f"***************************"
						bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
						response = requests.request("GET", bot_url)
						print("***************************")

					elif check_data1 is None and count_total_centers_for_PIN == total_centers_for_PIN and ommit_respose_with_zero_available_capacity_flag == 0:
						msg_start = f"No slots found now for your PIN {req} for age_limit {req_age}, we'll keep looking and notify you ASAP. Till then be safe!"
						bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
						response = requests.request("GET", bot_url)

	elif request[0].lower() == 'stop' :
		msg_start = stop_notification(chatid, messages)
		bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
		response = requests.request("GET", bot_url)

	else:
		msg_start = f"Please send your data in correct format i.e. PIN age_limit"
		bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(API_KEY, chatid, msg_start)
		response = requests.request("GET", bot_url)
		
