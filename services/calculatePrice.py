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
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "branch_id is required"})
        }
        return response
    
    if 'license_plate' not in data:
        logging.error("Validation Failed")
        response = {
            "statusCode": 402,
            "headers": {
                "Content-Type": "application/json"
            },
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
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "License plate not found"})
        }
        return response

    start_time = int(result['Item']['timestamp'])
    print(start_time)
    current_time = int(time.time())
    print(current_time)
    
    elapsed_minutes = round((current_time - start_time) / 60, 4)
    print(elapsed_minutes)
    
    fee_by_minute = float(os.environ["FEE_BY_MINUTE"])
    total = round(elapsed_minutes * fee_by_minute, 4)
    print(total)
    
    result['Item']['elapsed_minutes'] = elapsed_minutes
    result['Item']['total'] = total

    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(result['Item'], cls=decimalencoder.DecimalEncoder)
    }

    return response