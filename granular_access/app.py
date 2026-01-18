#!/usr/bin/env python3
# filepath: c:\Users\cratnaya\OneDrive\repos\amazon-quicksight-sdk-proserve\granular_access\app.py
from aws_cdk import App

from granular_access.granular_access_stack import GranularAccessStack


app = App()
GranularAccessStack(app, "granular-access")

app.synth()