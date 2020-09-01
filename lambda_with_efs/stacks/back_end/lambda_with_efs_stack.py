from aws_cdk import aws_apigateway as _apigw
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_logs as _logs

from aws_cdk import core

import os


class GlobalArgs:
    """
    Helper to define global statics
    """

    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = "lambda-with-efs"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_08_31"
    MIZTIIK_SUPPORT_EMAIL = ["mystique@example.com", ]


class LambdaWithEfsStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        vpc,
        efs_sg,
        efs_share,
        efs_ap,
        stack_log_level: str,
        back_end_api_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create Serverless Event Processor using Lambda):
        # Read Lambda Code):
        try:
            with open("lambda_with_efs/stacks/back_end/lambda_src/serverless_greeter.py", mode="r") as f:
                greeter_fn_code = f.read()
        except OSError as e:
            print("Unable to read Lambda Function Code")
            raise e

        greeter_fn = _lambda.Function(
            self,
            "secureGreeterFn",
            function_name=f"greeter_fn_{id}",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="index.lambda_handler",
            code=_lambda.InlineCode(greeter_fn_code),
            current_version_options={
                "removal_policy": core.RemovalPolicy.DESTROY,  # retain old versions
                "retry_attempts": 1,
                "description": "Mystique Factory Build Version"
            },
            timeout=core.Duration.seconds(15),
            reserved_concurrent_executions=20,
            retry_attempts=1,
            environment={
                "LOG_LEVEL": f"{stack_log_level}",
                "Environment": "Production",
                "ANDON_CORD_PULLED": "False",
                "RANDOM_SLEEP_ENABLED": "False"
            },
            description="A simple greeter function, which responds with a timestamp",
            vpc=vpc,
            vpc_subnets=_ec2.SubnetType.PRIVATE,
            security_groups=[efs_sg],
            filesystem=_lambda.FileSystem.from_efs_access_point(
                efs_ap, '/mnt/efs')
        )
        greeter_fn_version = greeter_fn.latest_version
        greeter_fn_dev_alias = _lambda.Alias(
            self,
            "greeterFnMystiqueAutomationAlias",
            alias_name="MystiqueAutomation",
            version=greeter_fn_version
        )

        # greeter_fn_version_alias = greeter_fn.current_version.add_alias("dev")
        # greeter_fn_prod_alias = greeter_fn.current_version.add_alias("prod")

        # Create Custom Loggroup
        # /aws/lambda/function-name
        greeter_fn_lg = _logs.LogGroup(
            self,
            "greeterFnLoggroup",
            log_group_name=f"/aws/lambda/{greeter_fn.function_name}",
            retention=_logs.RetentionDays.ONE_WEEK,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # Permissions to mount EFS (CDK May add them automatically)
        # roleStmt1 = _iam.PolicyStatement(
        #     effect=_iam.Effect.ALLOW,
        #     resources=[
        # f"arn:aws:elasticfilesystem:{core.Aws.REGION}:{core.Aws.ACCOUNT_ID}:file-system/{efs_share.file_system_id}"
        #     ],
        #     actions=["elasticfilesystem:*"]
        # )
        # roleStmt1.sid = "AllowLambdaToReadWriteToEfs"
        # greeter_fn.add_to_role_policy(roleStmt1)
# %%

        wa_api_logs = _logs.LogGroup(
            self,
            "waApiLogs",
            log_group_name=f"/aws/apigateway/{back_end_api_name}/access_logs",
            removal_policy=core.RemovalPolicy.DESTROY,
            retention=_logs.RetentionDays.ONE_DAY
        )

        #######################################
        ##    CONFIG FOR API STAGE : PROD    ##
        #######################################

        # Add API GW front end for the Lambda
        prod_api_stage_options = _apigw.StageOptions(
            stage_name="prod",
            throttling_rate_limit=10,
            throttling_burst_limit=100,
            # Log full requests/responses data
            data_trace_enabled=True,
            # Enable Detailed CloudWatch Metrics
            metrics_enabled=True,
            logging_level=_apigw.MethodLoggingLevel.INFO,
            access_log_destination=_apigw.LogGroupLogDestination(wa_api_logs),
            variables={
                "lambdaAlias": "prod",
                "appOwner": "Mystique"
            }
        )

        # Create API Gateway
        wa_api = _apigw.RestApi(
            self,
            "backEnd01Api",
            rest_api_name=f"{back_end_api_name}",
            deploy_options=prod_api_stage_options,
            endpoint_types=[
                _apigw.EndpointType.EDGE
            ],
            description=f"{GlobalArgs.OWNER}: API Best Practices. This stack deploys an API and integrates with Lambda $LATEST alias."
        )

        wa_api_res = wa_api.root.add_resource("well-architected-api")
        greetings_wall = wa_api_res.add_resource("message-wall")

        # Add GET method to API
        greetings_wall_get = greetings_wall.add_method(
            http_method="GET",
            request_parameters={
                "method.request.header.InvocationType": True,
                "method.request.path.mystique": True
            },
            integration=_apigw.LambdaIntegration(
                handler=greeter_fn,
                proxy=True
            )
        )

        # Add POST method to API
        greeter_method_get = greetings_wall.add_method(
            http_method="POST",
            request_parameters={
                "method.request.header.InvocationType": True,
                "method.request.path.mystique": True
            },
            integration=_apigw.LambdaIntegration(
                handler=greeter_fn,
                proxy=True
            )
        )

        # Add DELETE method to API
        greeter_method_get = greetings_wall.add_method(
            http_method="DELETE",
            request_parameters={
                "method.request.header.InvocationType": True,
                "method.request.path.mystique": True
            },
            integration=_apigw.LambdaIntegration(
                handler=greeter_fn,
                proxy=True
            )
        )

        # Outputs
        output_0 = core.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page."
        )

        output_1 = core.CfnOutput(
            self,
            "GreetingsWallApiUrl",
            value=f"{greetings_wall.url}",
            description="Use an utility like curl from the same VPC as the API to invoke it."
        )
