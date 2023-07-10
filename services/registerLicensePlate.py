import json
import boto3
import re
import random
from datetime import datetime
import time
import os

def handler(event, context):
    branches = ['LIM1', 'LIM2', 'LIM3', 'AQP1', 'AQP2', 'AQP3', 'CHI1', 'CHI2', 'CHI3']
    branch = random.choice(branches)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    detected_text = detect_text(key, bucket)
    license_plate = getLicensePlate(detected_text)

    if license_plate:
        print('License plate detected: ' + license_plate)
        registered_plate = register_plate(license_plate, branch)
        publish_event(registered_plate)
    else:
        print('No license plate detected')

    return json.dumps(detected_text)

def detect_text(photo, bucket):

    client = boto3.client('rekognition')
    response = client.detect_text(Image={'S3Object': {'Bucket': bucket, 'Name': photo}})
    textDetections = response['TextDetections']
    return textDetections

def getLicensePlate(textDetections):
    for text in textDetections:
        if text['Type'] == 'LINE':
            if re.match(r'^\w{3}-\d{3}$', text['DetectedText']):
                return text['DetectedText']

def register_plate(license_plate, branch):
    client = boto3.client("dynamodb")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp = int(time.time())
    table_name = os.environ["LICENSE_PLATES_TABLE_NAME"]

    response = client.put_item(
        TableName=table_name,
        Item={
            "branch_id": {"S": branch},
            "license_plate": {"S": license_plate},
            "create_date": {"S": now},
            "timestamp": {"N": str(timestamp)},
            "status": {"S": "CREATED"},
        }
    )

    return {
        "branch_id": branch,
        "license_plate": license_plate,
        "create_date": now,
        "timestamp": str(timestamp),
        "status": "CREATED"
    }

def publish_event(event):
    # Create an SNS client
    sns_client = boto3.client('sns')

    # Specify the ARN of the SNS topic you want to publish to
    topic_arn = 'arn:aws:sns:us-east-1:709220788877:dev-topic_license_plate_registered'

    # Convert the message dictionary to a JSON string
    message = json.dumps(event)

    # Publish the JSON message to the specified SNS topic
    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=message
    )

    return response