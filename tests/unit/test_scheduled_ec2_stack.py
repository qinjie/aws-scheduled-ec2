import aws_cdk as core
import aws_cdk.assertions as assertions

from scheduled_ec2.scheduled_ec2_stack import ScheduledEc2Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in scheduled_ec2/scheduled_ec2_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ScheduledEc2Stack(app, "scheduled-ec2")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
