import json
import os
import secrets
import requests
import boto3
from botocore.exceptions import ClientError
from mastodon import Mastodon

STATE_FILE = '/tmp/followed_hashtags.json'
BUCKET = os.environ['S3_BUCKET_NAME']
OBJECT_NAME = 'followed_hashtags.json'

S3_CLIENT = boto3.client('s3')


def get_state():
    try:
        S3_CLIENT.download_file(BUCKET, OBJECT_NAME, STATE_FILE)
    except ClientError:
        put_state(dict())

    try:
        with open(STATE_FILE, 'r') as infile:
            return json.load(infile)
    except FileNotFoundError:
        return dict()


def put_state(state):
    with open(STATE_FILE, 'w') as outfile:
        outfile.write(json.dumps(state))
    S3_CLIENT.upload_file(STATE_FILE, BUCKET, OBJECT_NAME)


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


def update_followed_hashtags(state, instance_list, current_hashtags):
    # Remove unlisted instances
    remove_unlisted_instances(state, instance_list)
    add_new_instances(state, instance_list)

    # Update tags per instance
    for instance in state:
        remove_unfollowed_hashtags(state[instance], current_hashtags)
        add_new_hashtags(state[instance], current_hashtags)

    # fetch new statuses
    new_status_urls = set()
    for instance in state:
        for hashtag in state[instance]:
            new_status_urls |= fetch_timeline(state[instance], instance, hashtag)

    return new_status_urls


def fetch_timeline(state, instance, hashtag):
    min_id = state[hashtag]
    mastodon = Mastodon(api_base_url=instance)
    statuses = mastodon.timeline_hashtag(hashtag, min_id=min_id)

    status_urls = set()
    max_id = 0
    for status in statuses:
        status_urls.add(status['url'])
        max_id = max(max_id, status['id'])
    if max_id > 0:
        state[hashtag] = max_id

    return status_urls


def add_new_hashtags(instance, current_hashtags):
    for hashtag in current_hashtags:
        if hashtag not in instance:
            instance[hashtag] = None


def remove_unfollowed_hashtags(instance, current_hashtags):
    to_remove = set()
    for hashtag in instance:
        if hashtag not in current_hashtags:
            to_remove.add(hashtag)

    for deleted_hashtag in to_remove:
        instance.pop(deleted_hashtag, None)


def remove_unlisted_instances(state, instance_list):
    to_remove = set()
    for instance in state:
        if instance not in instance_list:
            to_remove.add(instance)
    for deleted_instance in to_remove:
        state.pop(deleted_instance, None)


def add_new_instances(state, instance_list):
    for instance in instance_list:
        if instance not in state:
            state[instance] = dict()


def query_status_url(status_url):
    secret_values = secrets.get_secrets()
    mastodon = Mastodon(api_base_url=secret_values['query']['api_base_url'],
                        access_token=secret_values['query']['access_token'])
    mastodon.search_v2(status_url)
    print(status_url)


def lambda_handler(event, context):
    currently_followed_tags = get_all_followed_hashtags()
    state = get_state()
    instance_list = ['mastodon.social']
    new_status_urls = update_followed_hashtags(state, instance_list, currently_followed_tags)

    for status_url in new_status_urls:
        query_status_url(status_url)

    put_state(state)

    return {
        'statusCode': 200,
        'body': 'Done'
    }


if __name__ == '__main__':
    fakeEvent = {}
    lambda_handler(fakeEvent, None)
