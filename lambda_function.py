from __future__ import print_function
from newsapi import NewsApiClient
from random import randint
import boto3, botocore,  json


#-------API STUFF------------------------------------
API_KEY = "XXXXXXXXXXXXXX"
API_BASE = "https://newsapi.org/v2/everything?q="
headers = {'Content-Type' : 'application/json', 
		   'Authorization': 'Bearer {0}'.format(API_KEY)}
newsapi = NewsApiClient(api_key=API_KEY)
#-----------------------------------------------------

#------------AWS Client/Resource based objects. Don't change -----------------------
session = boto3.Session( 
    aws_access_key_id="XXXXXXXXXXXXXXXXX",
    aws_secret_access_key="XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    region_name='us-west-2')

sns_client = session.client('sns')
db_table = session.resource('dynamodb', region_name='us-west-2').Table('User_News_PrefDB')

#-----------------------------------------------------------------------------------

#------------------------------------------------------------------------
#Getting subscribing down
topic = sns_client.create_topic(Name='News-Notifications-System')
topic_arn = topic['TopicArn']
def subscribe_user_num(phonenumber):
	sns_client.subscribe(TopicArn=topic_arn,
		Protocol='sms',
		Endpoint=phonenumber
	)

def send_message(message, phonenum):
	#print(message)
	sns_client.publish(Message=message, PhoneNumber=phonenum)

#-----------------------------------------------------------------------------------
#Methods to test how API and SNS works
def deserialize_JSON_url(url):
	response = requests.get(url, headers=headers)
	if response.status_code == 200:
		return json.loads(response.content.decode('utf-8'))
	else:
		return None

def deserializeWithClient(query):
	top_headlines = newsapi.get_everything(q=query)
	return (top_headlines)



#------------------------------------------------------------------------
#Playing around with NewsAPI

#similar to SQL coalesce
def notNone(s,d):
    if s is None:
        return d
    else:
        return s

#returns the top headlines with a query in the form of a JSON string
def top_headlines_json(query):
	top_headlines = newsapi.get_top_headlines(q=query,
                                          language='en')
	return(json.dumps(top_headlines, indent=4))
	#print(top_headlines)

#headlines_json = top_headlines_json('Bitcoin')
#print(headlines_json)
#val = deserialize_JSON_url(api_url)

def format_request(article):
	retVal = '\tTITLE: ' + notNone(article['title'], "UNKNOWN") + '\n\tURL: ' + notNone(article['url'], "UNKNOWN")
	return retVal
	#return '\tTITLE: ' + article['title'] + '\n\tHEADLINE: ' + article['description'] + '\n\tAUTHOR: ' + notNone(article['author'], "UNKNOWN") + '\n\tURL: ' + article['url']'''

def get_top_headlines(category):
	newsArticles = newsapi.get_top_headlines(category=category, language='en', country='us')['articles']
	newsArticle = newsArticles[randint(0, len(newsArticles) - 1)]
	return format_request(newsArticle)

def get_everything(query):
	newsArticles = newsapi.get_everything(q=query,language='en', sort_by='relevancy')['articles']
	newsArticle = newsArticles[randint(0, len(newsArticles) - 1)]
	return format_request(newsArticle)


#This method should find the user in the db, and send them an alert according
#to what topics they are subscribed to
#sns_client.publish(Message=message, PhoneNumber='+14255305453')
def alert_user(user):
	message = list()
	formatted_msg = ""
	count = 0
	phoneNum = user['phone_num']

	topics, categories, topic, category = False, False, False, False  	
	#long method call to get a random category to use to get a news article  
	if 'topics' in user: 
		topics = user['topics']
		topic = topics.split(",")[randint(0, len(topics.split(",")) - 1)].strip()
	if 'categories' in user: 
		categories = user['categories']
		category = categories.split(",")[randint(0, len(categories.split(",")) - 1)].strip()
	
	while(count < 3):
		if (categories and not topics) or categories:
			category = categories.split(",")[randint(0, len(categories.split(",")) - 1)].strip()
			response = get_top_headlines(category)
			if response not in message and len(response) > 0: 
				message.append(response)
				count = count + 1
				if count == 4: break
		if  topics:
			topic = topics.split(",")[randint(0, len(topics.split(",")) - 1)].strip()
			response = get_everything(topic)
			if response not in message and len(response) > 0:
				message.append(response)
				count = count + 1
				if count == 4: break
	formatted_msg = 'Daily News!\n' + message[0] + "\n\n" + message[1] + "\n\n" + message[2]
	formatted_msg += "\nREPLY WITH 'STOP' to stop receiving daily news :'("
	print(phoneNum + '\n' + formatted_msg + '\n')
	send_message(formatted_msg, phoneNum)

def notify_all(users):
	try:
		while(users):
			alert_user(users.pop(0))
	except Exception:
		notify_all(users)
	#for user in users:
	#	alert_user(user)


def lambda_handler(event, context):
    notify_all(db_table.scan()['Items'])
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


if __name__ == "__main__":
	notify_all(db_table.scan()['Items'])