import boto3

def boto_resource(service, region):
    return boto3.resource(service, region_name=region)

def boto_client(service, region=None):
    """the boto3 service client is a lower-level construct compared to the boto3 resource client.
    it excludes some convenient functionality, like automatic pagination.
    prefer the service resource over the client"""
    return boto3.client(service, region_name=region)

def boto_conn(service, region=None, client=False):
    fn = boto_client if client else boto_resource
    return fn(service, region)
