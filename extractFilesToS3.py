import boto3
import zipfile
import io
import os

def lambda_handler(event, context):
    inputArt = event["CodePipeline.job"]["data"]["inputArtifacts"][0]
    cred = event["CodePipeline.job"]["data"]["artifactCredentials"]
    sourceBucket = inputArt["location"]["s3Location"]["bucketName"]
    key_name = inputArt["location"]["s3Location"]["objectKey"]
    ACCESS_KEY = cred["secretAccessKey"]
    SECRET_KEY =  cred["accessKeyId"]
    SESSION_TOKEN = cred["sessionToken"]
    
    s3 = boto3.resource("s3")
    #session = boto3.Session(
    #    aws_access_key_id=ACCESS_KEY,
    #    aws_secret_access_key=SECRET_KEY,
    #    aws_session_token=SESSION_TOKEN)
    
    #client = session.resource("s3")
    obj = s3.Bucket(sourceBucket).Object(key_name)

    #targetBucket = "flightzipper1"
    targetBucket = os.environ["targetBucket"]

    with io.BytesIO(obj.get()["Body"].read()) as file:
        with zipfile.ZipFile(file, mode='r') as zipf:
            for subfile in zipf.namelist():
                with zipf.open(subfile) as unzipped:
                    s3.Bucket(targetBucket).upload_fileobj(unzipped, subfile, ExtraArgs={'ContentType': 'text/html'})
    
    # We are done, lets inform CodePipeline
    codepipeline = boto3.client('codepipeline')
    codepipeline.put_job_success_result(jobId=event["CodePipeline.job"]["id"])
    
    return "success"