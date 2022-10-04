import boto3
import os
import json
from datetime import datetime

# Get current region of the lambda function
region_lambda = os.environ['AWS_REGION']


def lambda_handler(event, context):
    """
    Start/Stop EC2 instances which match a tag.
    """
    # Get tag name and tag values from event
    tag_name = event.get('tag_name', 'Schedule')
    tag_values = json.loads(event.get('tag_values', '["day", "night"]'))
    print(f'Tags: name={tag_name}, values={tag_values}')

    # Get region_name from event. Use lambda function region by default.
    region = event.get('region', region_lambda)
    ec2 = boto3.resource('ec2', region_name=region)

    # EC2 Tags used, e.g. tag_name = 'Schedule', tag values = ['day', 'night']
    filter_tags = {'Name': f'tag:{tag_name}', 'Values': tag_values}

    # Stop all running instances matching the tag
    filter_state = {'Name': 'instance-state-name', 'Values': ['running']}
    instances = ec2.instances.filter(Filters=[filter_state, filter_tags])
    for instance in instances:
        instance.stop()
        print(f'Stopped {instance.id}')

    # Start all stopped instances matching the tag
    filter_state = {'Name': 'instance-state-name', 'Values': ['stopped']}
    instances = ec2.instances.filter(Filters=[filter_state, filter_tags])
    for instance in instances:
        instance.start()
        print(f'Started {instance.id}')
