from __future__ import print_function # Python 2/3 compatibility
import boto3
import os
import json
import datetime
import botocore

def get_account_id():
    sts = boto3.client('sts')
    identity=sts.get_caller_identity()
    accountId = identity['Account']
    print('Default Credential Provider Chain Identity: ' + identity['Arn'])
    print("accountid "+accountId)
    return accountId
print('accountId is ' +get_account_id())
