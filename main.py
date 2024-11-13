# Import.

import random
import string
from google.cloud import datastore
from flask import Flask, redirect, jsonify, request, url_for
import requests
from urllib.parse import urlencode

# Config.

app = Flask(__name__)
CLIENT_ID = "1045061888846-5sog9v93ks3tcce7l93bt1qqplgolj7i.apps.googleusercontent.com"
CLIENT_SECRET = "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"
SCOPE = "https://www.googleapis.com/auth/userinfo.profile"
URL = "http://localhost:8080/"
REDIRECT_URI = URL + "redirect_url"

# Util.

def make_state():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def store_state(state):
    client = datastore.Client(project="cs493-a4-441522")
    kind = 'State'
    key = client.key(kind)
    entity = datastore.Entity(key=key)
    entity['name'] = state
    client.put(entity)

def check_if_state_exist(state):
    client = datastore.Client(project="cs493-a4-441522")
    query = client.query(kind='State')
    query.add_filter(filter=('name', '=', state))
    results = list(query.fetch())
    return len(results) > 0

# Function.

@app.route("/")
def main():
    return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Page Title</title>
        </head>
        <body>
            <a href="/auth">Sign in with Google</a>
        </body>
        </html>
    """

@app.route("/auth")
def auth():
    state = make_state()
    print("__________________________", state)
    store_state(state)
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'state': state,
        'prompt': 'consent',
        'include_granted_scopes': 'true'
    }
    url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
    return redirect(url)

# Get auth code + state.
# Check state.
# POST to get the auth token.
@app.route("/redirect_url")
def redirect_1():
    query_params = request.args
    state = query_params.get("state")
    print("__________________________", state)
    code = query_params.get("code")
    valid = check_if_state_exist(state)
    if valid == True:
        url = f"https://oauth2.googleapis.com/token?" \
            f"code={code}&" \
            f"client_id={CLIENT_ID}&" \
            f"client_secret={CLIENT_SECRET}&" \
            f"redirect_uri={REDIRECT_URI}&" \
            f"grant_type=authorization_code"
        response = requests.post(url)
        token_response = response.json()
        access_token = token_response.get("access_token")
        print(access_token)
        return redirect(url_for('display_info', access_token=access_token))

from flask import request, jsonify

@app.route("/display_info")
def display_info():
    access_token = request.args.get("access_token")
    
    # Set up the headers for the request with the provided access token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Make the request to get user info
    response = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers)
    
    # Check if the request was successful and the content is JSON
    if response.status_code == 200: #and response.headers.get('Content-Type') == 'application/json':
        user_info = response.json()
        name = user_info.get('name')
        last_name = user_info.get('family_name')
        return f"Name: {name}, Last Name: {last_name}"
    else:
        # If the response is not JSON or has an error, return the raw content for debugging
        return jsonify({"error": "Failed to retrieve user info", 
                        "status_code": response.status_code,
                        "content": response.text}), response.status_code


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
    