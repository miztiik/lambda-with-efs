from aws_cdk import core
from aws_cdk import aws_efs as _efs
from aws_cdk import aws_ec2 as _ec2


class GlobalArgs:
    """
    Helper to define global statics
    """

    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = "efs-io-performance"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_08_26"
    MIZTIIK_SUPPORT_EMAIL = ["mystique@example.com", ]


class EfsStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 vpc,
                 **kwargs
                 ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create Security Group to connect to EFS
        efs_sg = _ec2.SecurityGroup(
            self,
            id="efsSecurityGroup",
            vpc=vpc,
            security_group_name=f"efs_sg_{id}",
            description="Security Group to connect to EFS from the VPC"
        )

        efs_sg.add_ingress_rule(
            peer=_ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=_ec2.Port.tcp(2049),
            description="Allow EC2 instances within the same VPC to connect to EFS"
        )

        # Let us create the EFS Filesystem
        self.efs_file_system = _efs.FileSystem(
            self,
            "elasticFileSystem",
            file_system_name=f"high-performance-storage",
            vpc=vpc,
            security_group=efs_sg,
            encrypted=False,
            lifecycle_policy=_efs.LifecyclePolicy.AFTER_7_DAYS,
            performance_mode=_efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode=_efs.ThroughputMode.BURSTING,
            removal_policy=core.RemovalPolicy.DESTROY
        )



        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_0 = core.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page."
        )

        output_1 = core.CfnOutput(
            self,
            "MountEfs",
            value=f"sudo mount -t efs -o tls {self.efs_file_system.file_system_id}:/ /mnt/efs ",
            description="Use this command to mount efs using efs helper utility at location /mnt/efs"
        )