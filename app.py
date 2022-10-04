#!/usr/bin/env python3

import aws_cdk as cdk

from scheduled_ec2.scheduled_ec2_stack import ScheduledEc2Stack


app = cdk.App()
ScheduledEc2Stack(app, "ScheduledEc2Stack")

app.synth()
