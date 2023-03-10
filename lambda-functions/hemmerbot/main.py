from mastodon import Mastodon
import secrets
import os


def lambda_handler(event, context):

    secret_values = secrets.get_secrets()
    mastodon = Mastodon(api_base_url=secret_values['query']['api_base_url'],
                        access_token=secret_values['query']['access_token'])

    mastodon.toot('Helau!')

    return {
        'statusCode': 200,
        'body': 'Done'
    }


if __name__ == '__main__':
    fakeEvent = {'trends': ['mastodon.social', 'chaos.social']}
    lambda_handler(fakeEvent, None)
