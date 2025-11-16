import json
import boto3
import os

S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
s3 = boto3.client('s3')

cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}

def lambda_handler(event, context):
    try:
        parent_post_id = event['queryStringParameters'].get('postId')

        if not parent_post_id:
            return {'statusCode': 400, 'headers': cors_headers, 'body': json.dumps({'message': 'postId is required'})}

        # (สำคัญ) List ไฟล์เฉพาะในโฟลเดอร์ย่อย "posts/{post_id}/replies/"
        comment_prefix = f"posts/{parent_post_id}/replies/"
        response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=comment_prefix)

        all_replies = []

        if 'Contents' in response:
            for obj in response['Contents']:
                obj_key = obj['Key']
                if obj_key == comment_prefix: continue 

                reply_obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=obj_key)
                reply_data_str = reply_obj['Body'].read().decode('utf-8')
                reply_json = json.loads(reply_data_str)
                all_replies.append(reply_json)

        all_replies.sort(key=lambda x: x['createdAt'])

        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps(all_replies)
        }

    except Exception as e:
        return {'statusCode': 500, 'headers': cors_headers, 'body': json.dumps({'message': str(e)})}
