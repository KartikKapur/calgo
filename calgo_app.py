from flask import Flask
from flask import request, redirect
import json
import requests
from quickstart import *
import urllib
from webob import Response
from pymongo import MongoClient
app = Flask(__name__)
import sys
app.config['DEBUG'] = True


FB_APP_TOKEN= 'EAAPmvnm2ZAaUBABiID923tWjUnbxh7FgZCzLcCpHPZBEiLmOu98Yary2ZBJn2olkg6Kg8cLzbH02aIT1czTTAwvxkVt6P3ghz61mvwgfXgLlqi2vbQUAaS2ZAh2IF5bTmbwdiiV7has62AFpXZCKEsP6MbA5rhiTNg90yLVJZAw9wZDZD'
FB_ENDPOINT = 'https://graph.facebook.com/v2.6/me/{0}'
FB_MESSAGES_ENDPOINT = FB_ENDPOINT.format('messages')
FB_THREAD_SETTINGS_ENDPOINT = FB_ENDPOINT.format('thread_settings')


MONGO_DB_BEARMAX_DATABASE = 'calgo'
MONGO_DB_BEARMAX_ENDPOINT = 'ds019816.mlab.com'
MONGO_DB_BEARMAX_PORT = 19816

MONGO_DB_USERNAME = 'calgo'
MONGO_DB_PASSWORD = 'goingplaces'


def connect():
    connection = MongoClient(
        MONGO_DB_BEARMAX_ENDPOINT,
        MONGO_DB_BEARMAX_PORT
    )
    handle = connection[MONGO_DB_BEARMAX_DATABASE]
    handle.authenticate(
        MONGO_DB_USERNAME,
        MONGO_DB_PASSWORD
    )
    return handle


app = Flask(__name__)
app.config['DEBUG'] = True
handle = connect()

@app.route('/')
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == 'Calgo':
            return request.args.get('hub.challenge')
        else:
            return 'Wrong validation token'
    elif request.method == 'POST':
        data = json.loads(request.data)['entry'][0]['messaging']
        for i in range(len(data)):
            event = data[i]
            if 'sender' in event:
                print('Event: {0}'.format(event))
                sender_id = event['sender']['id']
                if 'message' in event and 'is_echo' in event['message'] and event['message']['is_echo']:
                    pass
                #  else handle.bot_users.find({'sender_id': sender_id}).count() == 0:
                else:
                    send_FB_text(sender_id, 'Hello, welcome to Calgo, you personal calender on messenger')
                    get_credentials()
                    init_bot_user(sender_id)
                # else:
                #     sender_id_matches = [x for x in handle.bot_users.find({'sender_id': sender_id})]
                #     if sender_id_matches:
                #         bot_user = sender_id_matches[0]
                #         handle_event(event,bot_user)
    return Response()


def handle_event(event, bot_user):
    if 'message' in event and 'text' in event['message']:
        message = event['message']['text']
        print('Message: {0}'.format(message))
        if message.isdigit():
            date = int(message)

        if 'quick_reply' in event['message']:
            handle_quick_replies(event['message']['quick_reply']['payload'],bot_user)


def handle_quick_replies(payload, bot_user):
    print('Payload: {0}'.format(payload))
    # if 'View:' in payload:

def send_FB_text(sender_id, text, quick_replies=None):
    message = {'text': text}
    if quick_replies:
        message['quick_replies'] = quick_replies
    return send_FB_message(sender_id,message)

def send_FB_message(sender_id, message):
    fb_response = requests.post(
        FB_MESSAGES_ENDPOINT,
        params={'access_token': FB_APP_TOKEN},
        data=json.dumps(
            {
                'recipient': {
                    'id': sender_id
                },
                'message': message
            }
        ),
        headers={'content-type': 'application/json'}
    )
    if not fb_response.ok:
        app.logger.warning('Not OK: {0}: {1}'.format(
            fb_response.status_code,
            fb_response.text
        ))

def init_bot_user(sender_id):
    send_FB_text(
        sender_id,
        'Would you like to view an event or create one? ',
        quick_replies=[
            {
                'content_type': 'text',
                'title': 'Create',
                'payload': 'do:Create'
            },
            {
                'content_type': 'text',
                'title': 'View',
                'payload': 'do:View'
            }
        ]
    )
    handle.bot_users.insert({
        'sender_id': sender_id,
        })

def send_FB_buttons(sender_id, text, buttons):
    return send_FB_message(
        sender_id,
        {'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'button',
                    'text': text,
                    'buttons': buttons}}})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)