from flask import Flask, render_template, request, redirect, url_for
from newsapi import NewsApiClient
import boto3, botocore 
from threading import Thread
import re

application = Flask(__name__)
application.secret_key = 'aoweirWE#(0wv9(#@()#'
numbers = {}

#-------API STUFF------------------------------------
API_KEY = "20e92f378d1444a5babc1b722935312d"
API_BASE = "https://newsapi.org/v2/everything?q="
headers = {'Content-Type' : 'application/json', 
		   'Authorization': 'Bearer {0}'.format(API_KEY)}
newsapi = NewsApiClient(api_key=API_KEY)
#-----------------------------------------------------

session = boto3.Session( 
    aws_access_key_id="XXXXXXXXXXXXXXXXX",
    aws_secret_access_key="XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    region_name='us-west-2')

db_table = session.resource('dynamodb', region_name='us-west-2').Table('User_News_PrefDB')
sns_client = session.client('sns')
topic = sns_client.create_topic(Name='News-Notifications-System')
topic_arn = topic['TopicArn']

@application.route('/', methods=['POST', 'GET'])
@application.route('/')
def subscribe():
	if request.method == 'POST':
		if request.form['button'] == 'Continue!':
			number = request.form['phone']
			if check_if_valid_phone(number):
				return redirect(url_for('phone', number=number))
			else:
				return render_template('home.html', error = "Invalid number")
				
	return render_template('home.html')

@application.route('/phone/<number>', methods=['POST', 'GET'])
def phone(number):
	error = None
	if number in numbers:
		topicList = numbers[number][0]
		categoryList = numbers[number][1]
	else:
		topicList = []
		categoryList = []
	
	if request.method == 'POST':
		print(request.form['button'])
		if request.form['button'] == 'Subscribe':
			if len(topicList) == 0 and len(categoryList) == 0:
				error = "Please choose at least one topic or category"
				return render_template("number.html", number=number, error=error, topics=topicList, categories=categoryList)
			elif not check_if_valid_phone(number):
				error = "The phone number you entered somehow got invalidated!"
				save_lists(number, topicList, categoryList)
				return render_template("number.html", number=number, error=error, topics=topicList, categories=categoryList)
			else:
				sns_client.subscribe(TopicArn=topic_arn,
					Protocol='sms',
					Endpoint='+1' + number
				)
				topics = " Topics: "
				for i in range(len(topicList)):
					if i == (len(topicList) - 1):
						topics += topicList[i]
					else:
						topics += topicList[i] + ","
				categories = " Categories: "
				for i in range(len(categoryList)):
					if i == (len(categoryList) - 1):
						categories += categoryList[i]
					else:
						categories += categoryList[i] + ","
						
				if len(categoryList) == 0 or len(topicList) == 0:
					if len(categoryList) == 0:
						db_table.put_item(Item={'phone_num' : '+1' + number, 'topics' : topics[8:]})
					elif len(topicList) == 0:
						db_table.put_item(Item={'phone_num' : '+1' + number,'categories' : categories[13:]})
				else:
					db_table.put_item(Item={'phone_num' : '+1' + number, 'topics' : topics[8:], 'categories' : categories[13:]})
				#clears the lists
				categoryList[:] = []
				topicList[:] = []
				save_lists(number, topicList, categoryList)
				return render_template("number.html", number=number, message="Successfully subscribed!", topics=topicList, categories=categoryList)


		if request.form['button'] == 'Add Topic':
			topic = str(request.form['topic'])
			print(topic)
			print(type(topic))
			resultNumber = newsapi.get_everything(q=topic,language='en', sort_by='relevancy')['totalResults']
			if resultNumber == 0:
				error = topic + " returned no results. Please choose another topic."
				save_lists(number, topicList, categoryList)
				return render_template("number.html", number=number, error=error, topics=topicList, categories=categoryList)
			
			else:
				if topic not in topicList:
					topicList.append(topic)
				message = topic + " added to topics!"
				save_lists(number, topicList, categoryList)
				return render_template("number.html", number=number, message=message, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "Business":
			if "business" not in categoryList:
				categoryList.append("business")
			message = "Business category added to your subscription!"
			save_lists(number, topicList, categoryList)
			return render_template("number.html", number=number, message=message, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "Entertainment":
			if "entertainment" not in categoryList:
				categoryList.append("entertainment")
			message = "Entertainment category added to your subscription!"
			save_lists(number, topicList, categoryList)
			return render_template("number.html", number=number, message=message, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "General":
			if "general" not in categoryList:
				categoryList.append("general")
			message = "General category added to your subscription!"
			save_lists(number, topicList, categoryList)
			return render_template("number.html", number=number, message=message, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "Health":
			if "health" not in categoryList:
				categoryList.append("health")
			message = "Health category added to your subscription!"
			save_lists(number, topicList, categoryList)
			return render_template("number.html", number=number, message=message, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "Science":
			if "science" not in categoryList:
				categoryList.append("science")
			message = "Science category added to your subscription!"
			save_lists(number, topicList, categoryList)
			return render_template("number.html", number=number, message=message, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "Sports":
			if "sports" not in categoryList:
				categoryList.append("sports")
			message = "Sports category added to your subscription!"
			save_lists(number, topicList, categoryList)
			return render_template("number.html", number=number, message=message, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "Technology":
			if "technology" not in categoryList:
				categoryList.append("technology")
			message = "Technology category added to your subscription!"
			save_lists(number, topicList, categoryList)
			return render_template("number.html", number=number, message=message, topics=topicList, categories=categoryList)
	save_lists(number, topicList, categoryList)
	return render_template("number.html", number=number, error=error, topics=topicList, categories=categoryList)
	
	
	
'''@application.route('/', methods=['POST', 'GET'])
@application.route('/')
def home():
	error = None
	if request.method == 'POST':
		if request.form['button'] == 'Subscribe!':
			if len(topicList) == 0 and len(categoryList) == 0:
				error = "Please choose at least one topic or category"
				return render_template("subscribe.html", error=error, topics=topicList, categories=categoryList)
			number = request.form['phone']
			if check_if_valid_phone(number):
				sns_client.subscribe(TopicArn=topic_arn,
					Protocol='sms',
					Endpoint=number
				)
				error = "This is a valid phone number"
				topics = " Topics: "
				for i in range(len(topicList)):
					if i == (len(topicList) - 1):
						topics += topicList[i]
					else:
						topics += topicList[i] + ","
				categories = " Categories: "
				for i in range(len(categoryList)):
					if i == (len(categoryList) - 1):
						categories += categoryList[i]
					else:
						categories += categoryList[i] + ","
				error += topics + categories
				if len(categoryList) == 0 or len(topicList) == 0:
					if len(categoryList) == 0:
						db_table.put_item(Item={'phone_num' : '+1' + number, 'topics' : topics[8:]})
					elif len(topicList) == 0:
						db_table.put_item(Item={'phone_num' : '+1' + number,'categories' : categories[13:]})
				else:
					db_table.put_item(Item={'phone_num' : '+1' + number, 'topics' : topics[8:], 'categories' : categories[13:]})
				#clears the lists
				categoryList[:] = []
				topicList[:] = []
				return render_template('subscribe.html', message="Successfully subscribed!", topics=topicList, categories=categoryList)

			# then we subscribe it
			else:
				error = number + " is not a valid phone number"
				return render_template('subscribe.html', error=error, topics=topicList, categories=categoryList)

		if request.form['button'] == 'Add Topic':
			topic = str(request.form['topic'])
			print(topic)
			print(type(topic))
			resultNumber = newsapi.get_everything(q=topic,language='en', sort_by='relevancy')['totalResults']
			if resultNumber == 0:
				error = topic + " returned no results. Please choose another topic."
				return render_template('subscribe.html', error=error, topics=topicList, categories=categoryList)
			
			else:
				if topic not in topicList:
					topicList.append(topic)
				error = topic + " added to topics!"
				return render_template('subscribe.html', message=error, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "Business":
			if "business" not in categoryList:
				categoryList.append("business")
			error = "Business category added to your subscription!"
			return render_template("subscribe.html",message=error, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "Entertainment":
			if "entertainment" not in categoryList:
				categoryList.append("entertainment")
			error = "Entertainment category added to your subscription!"
			return render_template("subscribe.html", message=error, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "General":
			if "general" not in categoryList:
				categoryList.append("general")
			error = "General category added to your subscription!"
			return render_template("subscribe.html", message=error, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "Health":
			if "health" not in categoryList:
				categoryList.append("health")
			error = "Health category added to your subscription!"
			return render_template("subscribe.html", message=error, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "Science":
			if "science" not in categoryList:
				categoryList.append("science")
			error = "Science category added to your subscription!"
			return render_template("subscribe.html", message=error, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "Sports":
			if "sports" not in categoryList:
				categoryList.append("sports")
			error = "Sports category added to your subscription!"
			return render_template("subscribe.html", message=error, topics=topicList, categories=categoryList)
		
		if request.form['button'] == "Technology":
			if "technology" not in categoryList:
				categoryList.append("technology")
			error = "Technology category added to your subscription!"
			return render_template("subscribe.html", message=error, topics=topicList, categories=categoryList)
		
	return render_template('subscribe.html', error=error, topics=topicList, categories=categoryList)
'''		
	
def save_lists(number, topics, categories):
	numbers[number] = [topics, categories]

def check_if_valid_phone(phonenumber):
	pattern = re.compile("^\D?(\d{3})\D?\D?(\d{3})\D?(\d{4})$")
	if re.match(pattern, phonenumber):
		return True
	else:
		return False


if __name__ == '__main__':
	application.run(debug=True, threaded=True)
