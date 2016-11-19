from flask import Flask
from flask import request, redirect
import json
import requests
import urllib
from webob import Response
from pymongo import MongoClient
app = Flask(__name__)
app.config['DEBUG'] = True

FB_APP_TOKEN= 'EAAPmvnm2ZAaUBAG852TcAX8FTZCwgeAiHLr6E8VZBniT8OUuLcKaBCZBMLiMxHNh5zQgKx7eOWMTCPyOGnJizZBi2qgyCwTxgqoY4nQeT6ljSFblqxvAyofd0VnY4iv296jIUGDZA7NlihX0h4pNeEvl57m2vrAVBnewCvi9l69AZDZD'
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
app.config['DEBUG'] = False
handle = connect()

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == 'bear':
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
                elif handle.bot_users.find({'sender_id': sender_id}).count() == 0:
                    send_FB_text(sender_id, 'Hello! I am Bearmax, your personal healthcare companion.')
    return Response


def send_FB_text(sender_id, text, quick_replies=None):
    message = {'text': text}
    # if quick_replies:
    #     message['quick_replies'] = quick_replies
    return send_FB_message(
        sender_id,
        message
    )

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
