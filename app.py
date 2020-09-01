#!/usr/bin/env python3

from aws_cdk import core

from lambda_with_efs.stacks.back_end.efs_stack import EfsStack
from lambda_with_efs.stacks.back_end.vpc_stack import VpcStack
from lambda_with_efs.stacks.back_end.lambda_with_efs_stack import LambdaWithEfsStack

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
    description="Miztiik Automation: Deploy AWS Elastic File System Stack"
)

# Lambda with EFS for Video Processing
lambda_with_efs = LambdaWithEfsStack(
    app,
    "lambda-with-efs",
    vpc=vpc_stack.vpc,
    efs_sg=efs_stack.efs_sg,
    efs_share=efs_stack.efs_share,
    efs_ap=efs_stack.efs_ap,
    stack_log_level="INFO",
    back_end_api_name="well-architected-api",
    description="Miztiik Automation: Lambda with EFS for Video Processing"
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
