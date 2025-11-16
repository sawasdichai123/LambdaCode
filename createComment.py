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
        token = auth_header.split(" ")[1] 
        decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        author_email = decoded['email'] 
        
        body = json.loads(event['body'])
        parent_post_id = body.get('postId') 
        comment_text = body.get('commentText')
        
        if not parent_post_id or not comment_text:
            return {'statusCode': 400, 'headers': cors_headers, 'body': json.dumps({'message': 'postId and commentText are required'})}

        comment_id = str(uuid.uuid4())
        timestamp_iso = datetime.datetime.utcnow().isoformat()
        
        comment_data = {
            'commentId': comment_id,
            'postId': parent_post_id,
            'commentText': comment_text,
            'authorEmail': author_email, 
            'createdAt': timestamp_iso
        }
        
        # ⬇️⬇️⬇️ (นี่คือจุดที่แก้ไข) ⬇️⬇️⬇️
        # เราจะบันทึก Reply ไว้ในโฟลเดอร์ของ Post แม่
        comment_key = f"posts/{parent_post_id}/replies/{comment_id}.json"
        # ⬆️⬆️⬆️ -------------------- ⬆️⬆️⬆️
        
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=comment_key,
            Body=json.dumps(comment_data),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 201, 
            'headers': cors_headers,
            'body': json.dumps(comment_data) 
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'headers': cors_headers, 'body': json.dumps({'message': str(e)})}
