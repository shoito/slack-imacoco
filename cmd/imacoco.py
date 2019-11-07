import json
import logging
import os
import re
from more_itertools import chunked
import requests

import boto3

from slackclient import SlackClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sc = SlackClient(os.environ['SLACK_TOKEN'])


def lambda_handler(event, context):
    logger.info(event)

    user = event['user']
    location = event['location']
    response_url = event['response_url']

    exec_command(user, location, response_url)


def build_message(error):
    if error == 'cannot_update_admin_user':
        message = '残念ながら「管理者」のあなたはパワフルすぎてimacocoで表示名を変更できません'
        logger.info(message)
        return message
    else:
        return 'imacocoに失敗しました'


def exec_command(user, location, response_url):
    logger.info('User: %s, Location: %s', user, location)

    try:
        api_response = update_display_name(user, location)
        if api_response['ok']:
            logger.info(api_response)
        else:
            logger.error(api_response)
            requests.post(response_url, json = {'text': build_message(api_response['error'])})
    except Exception as e:
        logger.error(e)


def update_display_name(user, location):
    user_info = get_display_name(user)
    if user_info['ok'] != True:
        logger.error('Failed users.profile.get: %s', user)
        return user_info

    profile = user_info['profile']
    logger.info('User: %s, Profile: %s', user, profile)

    display_name = profile['display_name'].split(' at ')[0]
    if location != 'reset':
        display_name = profile['display_name'].split(' at ')[0] + ' at ' + location

    return sc.api_call(
        'users.profile.set',
        user=user,
        profile={
            'display_name': display_name
        }
    )


def get_display_name(user):
    return sc.api_call(
        'users.profile.get',
        user=user,
        include_labels=True
    )
