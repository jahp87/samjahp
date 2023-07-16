import json
import boto3
#from aws_xray_sdk.core import xray_recorder
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths

logger = Logger(service="APP")
tracer = Tracer(service="APP")
app = APIGatewayRestResolver()


@app.get("/getinstance")
@tracer.capture_method
def getinstance():
    logger.info("Request received")
    ec2list = []
    # Get list of regions
    ec2 = boto3.client('ec2')
    regions = ec2.describe_regions().get('Regions',[] )

    # Iterate over regions
    for region in regions:

        print ("* Checking region  --   %s " % region['RegionName'])
        reg=region['RegionName']

        client = boto3.client('ec2', region_name=reg)
        response = client.describe_instances()

        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                print ("  ---- Instance %s in %s" % (instance['InstanceId'], region['RegionName']))
                ec2list.append(instance['InstanceId'])

    return {
        "statusCode": 200,
        "body": ec2list
    } 


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    return app.resolve(event, context)

    

