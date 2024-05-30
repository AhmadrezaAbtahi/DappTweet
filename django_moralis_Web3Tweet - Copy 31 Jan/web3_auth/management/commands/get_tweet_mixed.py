import time
import requests
from requests.auth import OAuth1
from django.conf import settings
from django.core.management.base import BaseCommand
from web3 import Web3

class Command(BaseCommand):
    help = 'Fetches input_data from the last Ethereum transaction and posts it as a tweet.'

    def handle(self, *args, **kwargs):
        w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
        
        last_processed_block = None

        def get_last_transaction_input(address):
            nonlocal last_processed_block
            current_block = w3.eth.blockNumber

            if last_processed_block is None:
                last_processed_block = current_block

            for block_num in range(current_block, last_processed_block, -1):
                block = w3.eth.getBlock(block_num, True)
                for tx in block.transactions:
                    if tx.to and tx.to.lower() == address.lower():
                        try:
                            decoded_input = bytes.fromhex(tx.input[2:]).decode('utf-8')  # stripping the '0x' and decoding
                            return decoded_input
                        except UnicodeDecodeError:
                            self.stdout.write("The input data couldn't be decoded using UTF-8!")
                            return None

            last_processed_block = current_block
            return None
        
        while True:
            tweet_text = get_last_transaction_input(settings.MONITORED_ETHEREUM_ADDRESS)

            if tweet_text:
                # Get Twitter Developer API credentials from Django settings
                CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY
                CONSUMER_SECRET = settings.TWITTER_CONSUMER_SECRET
                ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN
                ACCESS_TOKEN_SECRET = settings.TWITTER_ACCESS_TOKEN_SECRET

                # Set up the OAuth 1 authentication
                auth = OAuth1(
                    CONSUMER_KEY,
                    client_secret=CONSUMER_SECRET,
                    resource_owner_key=ACCESS_TOKEN,
                    resource_owner_secret=ACCESS_TOKEN_SECRET
                )

                # Define the API endpoint and tweet data
                endpoint_url = 'https://api.twitter.com/2/tweets'
                tweet_data = {
                    "text": tweet_text
                }

                # Send the request to post a tweet
                response = requests.post(endpoint_url, json=tweet_data, auth=auth)

                # Check the response
                if response.status_code == 201:
                    self.stdout.write(f"Successfully tweeted: {tweet_text}")
                else:
                    self.stdout.write(f"Error posting tweet: {response.text}")

            time.sleep(30)  # Check every 30 seconds
