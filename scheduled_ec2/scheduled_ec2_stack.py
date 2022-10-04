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

        # CloudFormation output
        CfnOutput(self, "LambdaFunctionRoleARN", value=role_lambda.role_arn)
        CfnOutput(self, "LambdaFunctionName", value=func.function_name)
        CfnOutput(self, "EventBridgeRuleName", value=rule.rule_name)
