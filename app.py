#!/usr/bin/env python3

from aws_cdk import core

from lambda_with_efs.stacks.efs_stack import EfsStack
from lambda_with_efs.stacks.vpc_stack import VpcStack
from lambda_with_efs.stacks.efs_performance_tester_stack import EfsPerformanceTesterStack

app = core.App()

# VPC Stack for hosting Secure API & Other resources
vpc_stack = VpcStack(
    app,
    "vpc-stack",
    description="Miztiik Automation: VPC to host resources for generating load on API"
)

# Create EFS
efs_stack = EfsStack(
    app,
    "efs-stack",
    vpc=vpc_stack.vpc,
    description="Mystique Automation: Deploy AWS Elastic File System Stack"
)

# EFS Best Practices & Performance Testing Amazon EFS
# lambda_with_efs = EfsIoPerformanceStack(
#     app,
#     "lambda-with-efs",
#     stack_log_level="INFO",
#     description="Miztiik Automation: EFS Best Practices & Performance Testing Amazon EFS"
# )

# Miztiik Automation: EFS Best Practices - Performance Testing Amazon EFS
efs_performance_tester_stack = EfsPerformanceTesterStack(
    app,
    "efs-performance-tester",
    vpc=vpc_stack.vpc,
    ec2_instance_type="t2.micro",
    stack_log_level="INFO",
    efs_id = efs_stack.efs_file_system.file_system_id,
    # api_url=secure_api_with_throttling.api_url,
    description="Miztiik Automation: EFS Best Practices - Performance Testing Amazon EFS"
)

# Stack Level Tagging
core.Tag.add(app, key="Owner",
             value=app.node.try_get_context("owner"))
core.Tag.add(app, key="OwnerProfile",
             value=app.node.try_get_context("github_profile"))
core.Tag.add(app, key="Project",
             value=app.node.try_get_context("service_name"))
core.Tag.add(app, key="GithubRepo",
             value=app.node.try_get_context("github_repo_url"))
core.Tag.add(app, key="Udemy",
             value=app.node.try_get_context("udemy_profile"))
core.Tag.add(app, key="SkillShare",
             value=app.node.try_get_context("skill_profile"))
core.Tag.add(app, key="AboutMe",
             value=app.node.try_get_context("about_me"))
core.Tag.add(app, key="BuyMeCoffee",
             value=app.node.try_get_context("ko_fi"))

app.synth()
