import json
import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource("sns")
    topic = sns.Topic("arn:aws:sns:us-east-1:913968646064:deployLekstugaTopic")
    
    location = {
        "bucketName": "lekstugebygge.johanhanses.net",
        "objectKey": "lekstugebygge"
    }
    try:
        job = event.get("CodePipeline.job")
        
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "BuildArtifact":
                    location = artifact["location"]["s3Location"]
            
    
        print("Building portfolio from " + str(location))
        
        s3 = boto3.resource("s3")
    
        lekstuge_bucket = s3.Bucket("lekstuga.johanhanses.net")
        bygge_bucket = s3.Bucket(location["bucketName"])
        
        lekstuge_zip = StringIO.StringIO()
        bygge_bucket.download_fileobj(location["objectKey"], lekstuge_zip)
        
        with zipfile.ZipFile(lekstuge_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                lekstuge_bucket.upload_fileobj(obj, nm, ExtraArgs={"ContentType": mimetypes.guess_type(nm)[0]})
                lekstuge_bucket.Object(nm).Acl().put(ACL="public-read")
        
        print("Job done!")
        topic.publish(Subject="Deploy message", Message="Lekstugan deployed succesfully")
        if job:
            codepipeline = boto3.client("codepipeline")
            codepipeline.put_job_success_result(jobId = job["id"])
    except:
        topic.publish(Subject="Deploy failed", Message="Lekstugan failade:(")
        raise
        

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }