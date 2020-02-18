import json
import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource("s3")

    lekstuge_bucket = s3.Bucket("lekstuga.johanhanses.net")
    bygge_bucket = s3.Bucket("lekstugebygge.johanhanses.net")
    
    lekstuge_zip = StringIO.StringIO()
    bygge_bucket.download_fileobj("lekstugebygge", lekstuge_zip)
    
    with zipfile.ZipFile(lekstuge_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            lekstuge_bucket.upload_fileobj(obj, nm, ExtraArgs={"ContentType": mimetypes.guess_type(nm)[0]})
            lekstuge_bucket.Object(nm).Acl().put(ACL="public-read")
    
    print("Job done!")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }