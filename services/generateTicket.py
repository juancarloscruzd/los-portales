import boto3
import json
def lambda_handler(event, context):
    messages = event['Records']
    

    # Process each received message
    for message in messages:
        body = message['body']
        
        print(f"Received message: {body}")

        bucket_name = "demo-parking-tickets	"
        encoded_string = json.dumps(body).encode("utf-8")
        file_name = body["license_plate"] + "-" + body["timestamp"] + ".txt"
        s3_path = file_name

        s3 = boto3.resource("s3")
        s3.Bucket(bucket_name).put_object(Key=s3_path, Body=encoded_string)