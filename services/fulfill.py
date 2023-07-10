import boto3
import json
import logging
from services import decimalencoder
import time
import uuid
import os

def handler(event, context):
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

    try:
        response_register_sale = register_sale(data['license_plate'], data['branch_id'], data['elapsed_minutes'], data['price'])
        response_update_plate_status = update_plate_status(data['license_plate'], data['branch_id'])
        publish_event(response_register_sale)
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "Sale registered", 
                                "sale": response_register_sale, 
                                "license_plate": response_update_plate_status})
        }
        return response
    
    except Exception as e:
        print(e)
        response = {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "Could not save sale"})
        }
        return response
    
def register_sale(license_plate, branch, elapsed_minutes, price):
    client = boto3.client("dynamodb")
    table_name = os.environ["SALES_TABLE_NAME"]
    id = str(uuid.uuid4())
    response = client.put_item(
        TableName=table_name,
        Item={
            "branch_id": {"S": branch},
            "sale_id": {"S": id},
            "license_plate": {"S": license_plate},
            "elapsed_minutes": {"N": str(elapsed_minutes)},
            "price": {"N": str(price)}
        }
    )

    return {
        "branch_id": branch,
        "sale_id": id,
        "license_plate": license_plate,
        "elapsed_minutes": str(elapsed_minutes),
        "price": str(price)
    }

def update_plate_status(license_plate, branch):
    client = boto3.client("dynamodb")
    table_name = os.environ["LICENSE_PLATES_TABLE_NAME"]
    
    update_expression = "SET #status_field = :status_value"
    expression_attribute_names = {'#status_field': 'status'}
    expression_attribute_values = {':status_value': {'S': 'PAID'}}
    
    response = client.update_item(
        TableName=table_name,
        Key={
            'branch_id': {'S': branch},
            'license_plate': {'S': license_plate}
        },
        UpdateExpression= update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues="UPDATED_NEW"
    )

    return response

def publish_event(event):
    # Create an SNS client
    sns_client = boto3.client('sns')

    # Specify the ARN of the SNS topic you want to publish to
    topic_arn = 'arn:aws:sns:us-east-1:709220788877:dev-topic_sale_registered'

    # Convert the message dictionary to a JSON string
    message = json.dumps(event)

    # Publish the JSON message to the specified SNS topic
    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=message
    )

    return response