#!/usr/bin/env python3

from aws_cdk import core

from efs_io_performance.efs_io_performance_stack import EfsIoPerformanceStack


app = core.App()
EfsIoPerformanceStack(app, "efs-io-performance")

app.synth()
