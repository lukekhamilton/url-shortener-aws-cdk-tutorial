import boto3
import json
import logging
import uuid
import os

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)


def main(event, context):
    LOG.info("EVENT: " + json.dumps(event))

    query_string_params = event["queryStringParameters"]

    if query_string_params is not None:
      target_url = query_string_params['targetUrl']
      if target_url is not None:
        return create_short_url(event)

    path_parameters = event['pathParameters']
    if path_parameters is not None:
      if path_parameters['proxy'] is not None:
        return read_short_url(event)

    return {
      'statusCode': 200,
      'body': 'usage: ?targetUrl=URL'
    }


def create_short_url(event):
    table_name = os.environ.get('TABLE_NAME')

    target_url = event["queryStringParameters"]["targetUrl"]

    id = str(uuid.uuid4())[0:8]

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(Item={
      'id': id,
      'target_url': target_url
    })

    url = "https://" \
          + event["requestContext"]["domainname"] \
          + event["requestContext"]["path"] \
          + id

    return {
      'statusCode': 200,
      'headers': {'Content-Type': 'text/plain'},
      'body': 'Created URL: %s' % url
    }

def read_short_url(event):
