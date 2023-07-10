import boto3
import json
import logging
from services import decimalencoder
import time
import os

def handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ["LICENSE_PLATES_TABLE_NAME"]
    table = dynamodb.Table(table_name)
    data = json.loads(event['body'])

    if 'branch_id' not in data:
        logging.error("Validation Failed")
        response = {
            "statusCode": 402,
            "body": json.dumps({"message": "branch_id is required"})
        }
        return response
    
    if 'license_plate' not in data:
        logging.error("Validation Failed")
        response = {
            "statusCode": 402,
            "body": json.dumps({"message": "license_plate is required"})
        }
        return response

    result = table.get_item(
        Key={
            'branch_id': data['branch_id'],
            'license_plate': data['license_plate']
        }
    )

    if 'Item' not in result:
        response = {
            "statusCode": 204,
            "body": json.dumps({"message": "License plate not found"})
        }
        return response

    status = str(result['Item']['status'])

    print(status)

    response = {}
    if status == 'CREATED':
        print("License plate registered but not paid")
        response = {
            "statusCode": 402,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"action": "CLOSE", "message": "License plate registered but not paid"})
        }
        return response
    else:
        print("License plate registered and paid")
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"action": "OPEN", "message": "License plate registered and paid"})
        }

    return response