import boto3

s3 = boto3.resource('s3')
## create bucket
s3.create_bucket(Bucket='qwerhegr')

target_bucket = s3.Bucket('qwerhegr')

## delete bucket
target_bucket.delete()

## update object
target_bucket.upload_file('./test', 'test')

## get object
target_object = target_bucket.Object('test')
object_content = target_object.get()['Body'].read().decode()

## delete object
target_object.delete()