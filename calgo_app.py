
from flask import Flask
from flask import request, redirect
import json
import requests
import urllib
from webob import Response

app = Flask(__name__)

@app.route('/')
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == 'bear':
            return request.args.get('hub.challenge')
        else:
            return 'Wrong validation token'

    return Response()
