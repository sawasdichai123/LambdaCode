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
        response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix='posts/')

        all_posts = []

        if 'Contents' in response:
            for obj in response['Contents']:
                obj_key = obj['Key']

                # (สำคัญ) ข้ามโฟลเดอร์ (posts/) และ ข้ามโฟลเดอร์ย่อย (replies/)
                if obj_key.endswith('/') or 'replies/' in obj_key:
                    continue 

                post_obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=obj_key)
                post_data_str = post_obj['Body'].read().decode('utf-8')
                post_json = json.loads(post_data_str)
                all_posts.append(post_json)

        all_posts.sort(key=lambda x: x['createdAt'], reverse=True)

        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps(all_posts)
        }

    except Exception as e:
        return {'statusCode': 500, 'headers': cors_headers, 'body': json.dumps({'message': str(e)})}
