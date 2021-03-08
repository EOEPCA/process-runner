import os
import requests
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth
from pystac import STAC_IO
from collections import namedtuple
import boto3
import botocore

S3Settings = namedtuple('S3Settings', ['region_name', 
                                       'endpoint_url', 
                                       'aws_access_key_id',
                                       'aws_secret_access_key'],
                        defaults=['fr-par',
                                  's3.fr-par.scw.cloud',
                                  None,
                                  None])

settings = S3Settings(aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], 
                      aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])



def stac_read_method(uri):

    parsed = urlparse(uri)

    if parsed.scheme == 's3':
    
        bucket = parsed.netloc
        key = parsed.path[1:]
    
        session = botocore.session.Session() 

        client = session.create_client(service_name='s3', 
                                       region_name=settings.region_name, 
                                       use_ssl=True, 
                                       endpoint_url=f'https://{settings.endpoint_url}',
                                       aws_access_key_id=settings.aws_access_key_id, 
                                       aws_secret_access_key=settings.aws_secret_access_key)
    
        
        return client.get_object(Bucket=bucket, Key=key)['Body'].read()


    if parsed.scheme.startswith('http'):

        if os.environ.get('STAGEIN_PASSWORD') is None:

            return requests.get(uri).text

        else:

            return requests.get(uri,
                                auth=HTTPBasicAuth(username=os.environ.get('STAGEIN_USERNAME'),
                                                   password=os.environ.get('STAGEIN_PASSWORD'))
                                ).text
    else:

        return STAC_IO.default_read_text_method(uri)
