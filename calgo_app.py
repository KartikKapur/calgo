from flask import Flask
from flask import request, redirect
import json
import requests
import urllib
from webob import Response
import os
import sys
from pymongo import MongoClient



FB_APP_TOKEN = 'EAAPmvnm2ZAaUBADCZCBCQL9tMkf7tLyVJxdezJeKPjwOa1uYsgcaK0eZCFiVOcoGhms5M7580ZCCXHAuZBczzdOmaeEjLgnMCoiyM9BwxmZCuqsXlSlmeOW8DnfLDq0CK23HTxBv44QGAjQYPUPBC1yRql66J2S80YEjSU7QZBHGAZDZD'
FB_ENDPOINT = 'https://graph.facebook.com/v2.6/me/{0}'
FB_MESSAGES_ENDPOINT = FB_ENDPOINT.format('messages')
FB_THREAD_SETTINGS_ENDPOINT = FB_ENDPOINT.format('thread_settings')
# MONGO_DB_BEARMAX_DATABASE = ' '
# MONGO_DB_BEARMAX_ENDPOINT = ' '
# MONGO_DB_BEARMAX_PORT = ''
# MONGO_DB_USERNAME = ' '
# MONGO_DB_PASSWORD = ' '

app = Flask(__name__)
def connect():
    connection = MongoClient(
    #     MONGO_DB_BEARMAX_ENDPOINT,
    #     MONGO_DB_BEARMAX_PORT
    # )
    # handle = connection[MONGO_DB_BEARMAX_DATABASE]
    # handle.authenticate(
    #     MONGO_DB_USERNAME,
    #     MONGO_DB_PASSWORD
    )
    return handle

app = Flask(__name__)
app.config['DEBUG'] = True
handle = connect()


@app.route('/')
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == 'calgo':
            return request.args.get('hub.challenge')
        else:
            return 'Wrong validation token'
    elif request.method =='POST':
        data = json.loads(request.data)['entry'][0]['messaging']
        for i in range(len(data)):
            event = data[i]
            if 'sender' in event:
                print('Event: {0}'.format(event))
                sender_id = event['sender']['id']
                if 'message' in event and 'is_echo' in event['message'] and event['message']['is_echo']:
                    pass
                else:
                    send_FB_text(sender_id, 'Hello! I am Bearmax, your personal healthcare companion.')
                    init_bot_user(sender_id)

    return Response()


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
            fb_response.text))

def send_FB_text(sender_id, text, quick_replies=None):
    message = {'text': text}
    if quick_replies:
        message['quick_replies'] = quick_replies
    return send_FB_message(
        sender_id,
        message)




def send_FB_buttons(sender_id, text, buttons):
    return send_FB_message(
        sender_id,
        {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'button',
                    'text': text,
                    'buttons': buttons
                }}})

def init_bot_user(sender_id):
    send_FB_text(
        sender_id,
        'Do you want to view your events or make one?',
        quick_replies=[
            {
                'content_type': 'text',
                'title': 'View',
                'payload': ''
            },
            {
                'content_type': 'text',
                'title': 'Make',
                'payload': 'Gender:make'
            }
        ]
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
