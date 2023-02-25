import json
import secrets
import requests

CONFIG_FILE = 'followed_hashtags.py.json'


def get_config():
    with open(CONFIG_FILE, 'r') as infile:
        return json.load(infile)


def get_user_followed_hashtags(api_base_url, access_token):
    try:
        url = "https://%s/api/v1/followed_tags" % api_base_url
        auth = "Bearer %s" % access_token
        headers = {'Authorization': auth}
        payload = {'limit': '20'}
        r = requests.get(url=url, headers=headers, params=payload)
        hashtags = set()
        for item in r.json():
            hashtags.add(item['name'])
        return hashtags
    except:
        return set()


def get_all_followed_hashtags():
    secret_values = secrets.get_secrets()
    hashtags = set()
    users = secret_values['users_following_hashtags']
    for instance in users:
        for username in users[instance]:
            token = users[instance][username]
            hashtags |= get_user_followed_hashtags(instance, token)
    return hashtags


def lambda_handler(event, context):
    print(get_all_followed_hashtags())

    return {
        'statusCode': 200,
        'body': 'Done'
    }


if __name__ == '__main__':
    fakeEvent = {}
    lambda_handler(fakeEvent, None)
