import json
import boto3
import bcrypt
import jwt
import os
import datetime

S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
JWT_SECRET = os.environ.get('JWT_SECRET')
s3 = boto3.client('s3')

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

        if not email or not password:
            return {'statusCode': 400, 'headers': cors_headers, 'body': json.dumps({'message': 'Email and password are required'})}

        if not S3_BUCKET_NAME or not JWT_SECRET:
            return {'statusCode': 500, 'headers': cors_headers, 'body': json.dumps({'message': 'Server configuration error (missing env vars)'})}

        user_key = f"users/{email}.json"
        try:
            response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=user_key)
            user = json.loads(response['Body'].read().decode('utf-8'))
        except s3.exceptions.NoSuchKey:
            return {'statusCode': 404, 'headers': cors_headers, 'body': json.dumps({'message': 'User not found'})}

        stored_hash = user['password_hash'].encode('utf-8')

        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            payload = {
                'email': user['email'], # (Token ใช้ email)
                'iat': datetime.datetime.utcnow(),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'message': 'Login successful', 'token': token})}
        else:
            return {'statusCode': 401, 'headers': cors_headers, 'body': json.dumps({'message': 'Invalid credentials'})}

    except Exception as e:
        return {'statusCode': 500, 'headers': cors_headers, 'body': json.dumps({'message': str(e)})}
