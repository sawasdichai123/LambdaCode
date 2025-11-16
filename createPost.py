import json
import boto3
import jwt
import os
import uuid
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
        auth_header = event['headers'].get('Authorization')
        token = auth_header.split(" ")[1] # "Bearer <token>"
        decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        author_email = decoded['email']

        body = json.loads(event['body'])
        comment_text = body.get('commentText') # (รับ commentText)

        if not comment_text:
            return {'statusCode': 400, 'headers': cors_headers, 'body': json.dumps({'message': 'Comment text is required'})}

        post_id = str(uuid.uuid4())
        timestamp_iso = datetime.datetime.utcnow().isoformat()

        post_data = {
            'postId': post_id,
            'authorEmail': author_email,
            'commentText': comment_text,
            'createdAt': timestamp_iso
        }

        post_key = f"posts/{post_id}.json" # (บันทึกในโฟลเดอร์ posts/)
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=post_key,
            Body=json.dumps(post_data),
            ContentType='application/json'
        )

        return {'statusCode': 201, 'headers': cors_headers, 'body': json.dumps(post_data)}

    except Exception as e:
        return {'statusCode': 500, 'headers': cors_headers, 'body': json.dumps({'message': str(e)})}

