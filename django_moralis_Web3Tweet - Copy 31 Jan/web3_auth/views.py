import json
import requests
import oauthlib.oauth1
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from moralis import evm_api

def homepage(request):
    return render(request, 'homepage.html', {})

def publish_message(request):
    return render(request, 'publish_message.html')

def transaction_detail(request):
    if request.method == 'POST':
        transaction_hash = request.POST.get('transaction_hash')
        params = {
            "transaction_hash": transaction_hash,
            "chain": "sepolia",
        }

        result = evm_api.transaction.get_transaction(
            settings.API_KEY,
            params,
        )

        input_hex = result.get('input')
        input = bytes.fromhex(input_hex[2:]).decode('utf-8')

        from_address = result.get('from_address')

        return render(request, 'transaction_detail.html', {'input': input, 'from_address' : from_address })
        
    return render(request, 'homepage.html', {})


# Twitter API credentials from settings.py
consumer_key = settings.TWITTER_CONSUMER_KEY
consumer_secret = settings.TWITTER_CONSUMER_SECRET
access_token = settings.TWITTER_ACCESS_TOKEN
access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET

@require_http_methods(["GET", "POST"])
def send_direct_message(request):
    if request.method == "POST":
        username = request.POST.get('twitter_username')
        text = request.POST.get('message')

        # Setup OAuth1 Authentication for getting user ID
        auth = oauthlib.oauth1.Client(consumer_key, client_secret=consumer_secret,
                                      resource_owner_key=access_token, resource_owner_secret=access_token_secret,
                                      signature_method=oauthlib.oauth1.SIGNATURE_HMAC, signature_type=oauthlib.oauth1.SIGNATURE_TYPE_AUTH_HEADER)

        # Preparing the request for getting user ID
        user_id_url, user_id_headers, _ = auth.sign(f"https://api.twitter.com/2/users/by/username/{username}", http_method="GET")

        # Making the request for getting user ID
        response = requests.get(user_id_url, headers=user_id_headers)

        if response.status_code == 200:
            user_data = response.json()
            recipient_id = user_data['data']['id']

            # Endpoint URL for sending DM
            dm_url = f"https://api.twitter.com/2/dm_conversations/with/{recipient_id}/messages"

            # Payload for DM
            dm_payload = json.dumps({"text": text})
            dm_headers = {'Content-Type': 'application/json'}

            # Preparing and signing the DM request
            dm_uri, dm_headers, dm_body = auth.sign(dm_url, http_method="POST", body=dm_payload, headers=dm_headers)

            # Making the DM request
            dm_response = requests.post(dm_uri, headers=dm_headers, data=dm_body)
            return HttpResponse(dm_response.text)
        else:
            return HttpResponse("Failed to fetch user ID")
    else:
        return render(request, 'send_direct_message.html')
