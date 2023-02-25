import json

SECRETS_FILE = 'secrets.json'


def get_secrets():
    with open(SECRETS_FILE, 'r') as infile:
        return json.load(infile)

