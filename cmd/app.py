import json
import logging
import os
from base64 import b64decode
from urllib.parse import parse_qs

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

EXEC_LAMBDA_NAME = os.environ['EXEC_LAMBDA_NAME']
VERIFICATION_TOKEN = os.environ['VERIFICATION_TOKEN']

# ENCRYPTED_EXPECTED_TOKEN = os.environ['KMS_ENCRYPTED_TOKEN']
# expected_token = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_EXPECTED_TOKEN))['Plaintext'].decode()

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    if not 'body' in event:
        return respond('Request body is empty')

    params = parse_qs(event['body'])
    token = params['token'][0]
    if token != VERIFICATION_TOKEN:
        logger.error('Request token (%s) does not match expected', token)
        return respond('Invalid request token')

    logger.info(params)
    if not is_valid(params):
        logger.error('Invalid command parmas: %s', params)
        return respond('''usage:
\t/imacoco 佐久間\n
\t/imacoco reset
        ''')

    location = ''
    if 'text' in params:
        location = params['text'][0]

    lambda_client.invoke(
        FunctionName = EXEC_LAMBDA_NAME,
        InvocationType = 'Event',
        Payload = json.dumps({
            'user': params['user_id'][0],
            'location': location,
            'response_url': params['response_url'][0],
        }, ensure_ascii = False)
    )

    return respond()

def is_valid(params):
    if 'text' not in params:
        return False

    return True

def respond(res = None):
    return {
        'statusCode': '200',
        'body': res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }