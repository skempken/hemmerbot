import json
import secret
import requests
import os
import boto3

TMP_FILE = '/tmp/statuses.json'
BUCKET = os.environ['S3_BUCKET_NAME']
OBJECT_NAME = 'statuses.json'

S3_CLIENT = boto3.client('s3')

def get_trending(instance):
    try:
        url = "https://%s/api/v1/trends/statuses" % instance
        headers = {'Accept-language': 'de-DE,de;q=0.9'}
        payload = {'limit': '20'}
        r = requests.get(url=url, headers=headers, params=payload)
        status_urls = set()
        for item in r.json():
            status_urls.add(item['url'])
        return status_urls
    except:
        return set()


def search_status(instance, access_token, status):
    url = "https://%s/api/v2/search" % instance
    auth = "Bearer %s" % access_token
    headers = {'Authorization': auth}
    payload = {'q': status, 'resolve': 'true', 'limit': '5'}
    r = requests.get(url=url, headers=headers, params=payload)


def get_queried():
    pull_s3(TMP_FILE)

    try:
        with open(TMP_FILE, "r") as infile:
            json_object = json.load(infile)
        return set(json_object)
    except FileNotFoundError:
        return set()


def put_queried(status_urls):
    json_object = json.dumps(list(status_urls), indent=4)
    with open(TMP_FILE, "w") as outfile:
        outfile.write(json_object)

    push_s3(TMP_FILE)
    return

def search_statuses(instance, access_token, status_urls):
    for status_url in status_urls:
        print(status_url)
        search_status(instance, access_token, status_url)


def push_s3(file):
    S3_CLIENT.upload_file(file, BUCKET, OBJECT_NAME)
    return


def pull_s3(file):
    S3_CLIENT.download_file(BUCKET, OBJECT_NAME, file)
    return


def lambda_handler(event, context):
    secret_values = secret.get_secrets()
    api_base_url = secret_values['api_base_url']
    access_token = secret_values['access_token']

    instances = ['mastodon.social', 'chaos.social', 'det.social']

    status_urls = set()
    for instance in instances:
        status_urls |= get_trending(instance)

    to_search = status_urls - get_queried()
    put_queried(status_urls)

    search_statuses(api_base_url, access_token, to_search)

    return {
        'statusCode': 200,
        'body': 'Done'
    }


if __name__ == '__main__':
    fakeEvent = {}
    lambda_handler(fakeEvent, None)
