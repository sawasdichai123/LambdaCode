registerUser

import json
import boto3
import bcrypt
import os

S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
s3 = boto3.client('s3')

# (สำคัญ) นี่คือ Headers ที่แก้ปัญหา CORS
cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body.get('email') 
        password = body.get('password')

        if not email or not password or not S3_BUCKET_NAME:
            # (สำคัญ) ต้องมี 'headers' และ 'body' ที่มี 'message'
            return {'statusCode': 400, 'headers': cors_headers, 'body': json.dumps({'message': 'Email, password, and S3_BUCKET_NAME env var are required'})}

        if len(password) < 8:
            return {'statusCode': 400, 'headers': cors_headers, 'body': json.dumps({'message': 'Password must be at least 8 characters long'})}

        user_key = f"users/{email}.json"
        try:
            s3.head_object(Bucket=S3_BUCKET_NAME, Key=user_key)
            # (สำคัญ) ต้องมี 'headers' และ 'body' ที่มี 'message'
            return {'statusCode': 409, 'headers': cors_headers, 'body': json.dumps({'message': 'This email is already registered'})}
        except s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] != '404':
                raise 

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        user_data = {
            'email': email,
            'password_hash': hashed_password.decode('utf-8')
        }

        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=user_key,
            Body=json.dumps(user_data),
            ContentType='application/json'
        )

        return {'statusCode': 201, 'headers': cors_headers, 'body': json.dumps({'message': 'User registered successfully'})}

    except Exception as e:
        print(f"Error: {str(e)}")
        # (สำคัญ) ต้องมี 'headers' และ 'body' ที่มี 'message'
        return {'statusCode': 500, 'headers': cors_headers, 'body': json.dumps({'message': str(e)})}
