# Run/Stop EC2 with EventBridge

**Tags:** 

* AWS, Python, Mac/Linux
* Lambda, EventBridge, CDK

**Pre-requists:**

* [Setup AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)



Ideally, we should run on-demand EC2 instances only when they are in use. If the usage of these EC2 instances has a fixed schedule, for convenience, we can use a schedule job to start/stop them.

In this article, I implements a Lambda function to start/stop EC2 instance(s). The triggering of lambda function is scheduled by an EventBridge schedule. EC2 instances are filtered by a tag. 

This project is deployed using AWS CDK.

### Initialize Project

1. Create a project folder `scheduled-ec2` and initialize a new CDK project in Python language.

   ```
   mkdir scheduled-ec2 && cd scheduled-ec2
   cdk init --language=python
   ```

2. CDK project will create a virtual environment in the `.venv` subfolder. Activate the virtual environment and install dependencies.

   ```
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Start the project in Visual Studio Code.

   ```
   code .
   ```

### Create a Simple Lambda Function

1. Create a new folder `lambda` which will contain the code for lambda function.

2. Create a file `lambda_function.py` in the `lambda` folder.

   ```
   ├── lambda
   │   ├── lambda_function.py
   ├── scheduled_ec2
   ```

3. Update the `lambda_function.py` with following demo code, which prints current date time.

   ```python
   from datetime import datetime 
   
   def lambda_handler(event, context):
       print(datetime.now().isoformat())
   ```

### Deploy the Lambda Function

We will deploy a Lambda function with a EventBridge rule using CDK.

1. Update `scheduled_ec2/scheduled_ec2_stack.py` file 

   ```python
   from aws_cdk import (
       Stack,
       aws_iam as iam,
       aws_events as events,
       aws_events_targets as targets,
       aws_lambda as lambda_,
   )
   from constructs import Construct
   
   
   class ScheduledEc2Stack(Stack):
   
       def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
           super().__init__(scope, construct_id, **kwargs)
   
           # Create new IAM role for Lambda function
           role_lambda = iam.Role(
               self, 'LambdaStartStopEc2',
               assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
           )
           role_lambda.add_to_policy(iam.PolicyStatement(
               resources=["arn:aws:logs:*:*:*"],
               actions=[
                   "logs:CreateLogGroup",
                   "logs:CreateLogStream",
                   "logs:PutLogEvents"
               ]
           ))
   
           # Create Lambda function from local folder
           func = lambda_.Function(
               self, 'StartStopEc2',
               runtime=lambda_.Runtime.PYTHON_3_9,
               handler="lambda_function.lambda_handler",
               code=lambda_.AssetCode.from_asset('lambda'),
               role=role_lambda
           )
   
           # Create an EventBridge rule
           rule = events.Rule(
               self, "StartStopEc2Schedule",
               schedule=events.Schedule.expression('cron(* * * * ? *)')
           )
           target = targets.LambdaFunction(func)
           rule.add_target(target)
   ```

2. Use `cdk synth` to make sure there is no error in CDK project.

   ```bash
   cdk synth
   ```

3. Deploy the CDK project.

   ```bash
   cdk deploy
   ```

4. Login into AWS Console. Go to EventBridge > Rules. There is a new rule `ScheduledEc2Stack-*`, which is scheduled to run every minute.

   ![image-20221004111723756](https://raw.githubusercontent.com/qinjie/picgo-images-2/master/img/image-20221004111723756.png)

5. Check the Targets of this schedule, which is currently pointing to our lambda function. Click on the link to view the target Lambda function.

   ![image-20221004112137282](https://raw.githubusercontent.com/qinjie/picgo-images-2/master/img/image-20221004112137282.png)

6. Examine the lamba function's logs. 

   ![image-20221004113035652](https://raw.githubusercontent.com/qinjie/picgo-images-2/master/img/image-20221004113035652.png)

7. If it logs a datetime string, that means it is triggered by EventBridge rule and executed sucessfully. 

   ![image-20221004113001561](https://raw.githubusercontent.com/qinjie/picgo-images-2/master/img/image-20221004113001561.png)



### Update CDK Project

Modify the `schedule_ec2_stack.py` file with following code.

```python
from aws_cdk import (
    Stack, CfnOutput,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as lambda_,
)
from constructs import Construct

class ScheduledEc2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create new IAM role for Lambda function
        role_lambda = iam.Role(
            self, 'LambdaStartStopEc2',
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        role_lambda.add_to_policy(iam.PolicyStatement(
            resources=["arn:aws:logs:*:*:*"],
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ]
        ))
        # Grant role permissions to list/start/stop EC2 instances
        role_lambda.add_to_policy(iam.PolicyStatement(
            resources=["*"],
            actions=[
                "ec2:DescribeInstances",
                "ec2:StartInstances",
                "ec2:DescribeTags",
                "ec2:DescribeInstanceTypes",
                "ec2:StopInstances",
                "ec2:DescribeInstanceStatus"
            ],
        ))

        # Create function from local folder
        func = lambda_.Function(
            self, 'StartStopEc2',
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=lambda_.AssetCode.from_asset('lambda'),
            role=role_lambda
        )

        # Create an EventBridge rule
        rule = events.Rule(
            self, "StartStopEc2Schedule",
            schedule=events.Schedule.expression('cron(0 23,10 * * ? *)')
        )
        target_event = events.RuleTargetInput.from_object(
            {'tag_name': 'Schedule', 'taget_values': '["day", "night"]'}
        )
        target = targets.LambdaFunction(func, event=target_event)
        rule.add_target(target)
```

Following are the changes to the code.

1. Add a policy to the IAM role such that lambda function has rights to access EC2 service.

   ```python
           # Grant role permissions to list/start/stop EC2 instances
           role_lambda.add_to_policy(iam.PolicyStatement(
               resources=["*"],
               actions=[
                   "ec2:DescribeInstances",
                   "ec2:StartInstances",
                   "ec2:DescribeTags",
                   "ec2:DescribeInstanceTypes",
                   "ec2:StopInstances",
                   "ec2:DescribeInstanceStatus"
               ],
           ))
   ```

2. Update the rule to execute it twice a day. For example, schedule it to be on 2300UTC and 1000UTC. 

   ```python
           # Create an EventBridge rule
           rule = events.Rule(
               self, "StartStopEc2Schedule",
               schedule=events.Schedule.expression('cron(0 23,10 * * ? *)')
           )
   ```

3. Provide an event object so that we can pass inputs to lambda function. For example, set the `event` parameter to have `tag_name` and `tag_values` attributes.

   ```python
           target_event = events.RuleTargetInput.from_object(
               {'tag_name': 'Schedule', 'taget_values': '["day", "night"]'}
           )
           target = targets.LambdaFunction(func, event=target_event)
           rule.add_target(target)
   ```

4. Re-deploy the CDK project.

   ```bash
   cdk deploy
   ```



### Update Lambda Function

Modify `lambda/lambda_function.py` to update the Lambda function.

```python
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
```

Here are what the code does.

* It uses EC2 Resource object to filter EC2 instances by its state and tag. 
* It uses the `tag_name` and `tag_values` from input `event` to construct a filter.
* It then stop all running instances which matches the tag. 
* It also start all stopped instances which matches the tag.



### Test Lambda Function

1. Create an EC2 instance in the same region as the lambda function.
2. Add a tage to EC2.
   * Tag name: `Schedule`
   * Tag value: `day` or `night`

3. Wait for EC2 instance to be in `running` status.
4. Test the lambda function without modifying input.
5. Observe the status of EC2 instance changed to `stopping` then `stopped`.
6. You can run test the lambda function again and it will start the EC2 instance.



### Deploy Final CDK Project

Finally, deploy CDK project with final code.

```bash
cdk deploy
```



### Conclusion

In this project, we deploy a lambda function to toggle the state of EC2 instances in the same region. It uses tag to filter the EC2 instances. We also setup an EventBridge rule to run the Lambda function at schedule.
