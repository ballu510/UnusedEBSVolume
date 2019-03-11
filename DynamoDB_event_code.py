#
#  Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#  This file is licensed under the Apache License, Version 2.0 (the "License").
#  You may not use this file except in compliance with the License. A copy of
#  the License is located at
# 
#  http://aws.amazon.com/apache2.0/
# 
#  This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
#  CONDITIONS OF ANY KIND, either express or implied. See the License for the
#  specific language governing permissions and limitations under the License.
#
from __future__ import print_function # Python 2/3 compatibility
import boto3
import os
import json
import datetime
import botocore
import time
from botocore.exceptions import ClientError

# get AWS account id to concatenate with the DDB table name
def get_account_id():
    sts = boto3.client('sts')
    identity=sts.get_caller_identity()  
    accountId = identity['Account']
    print('Default Credential Provider Chain Identity: ' + identity['Arn'])
    print("accountid "+accountId)
    return accountId
    
print('accountId is ' +get_account_id())


def lambda_handler(event,context):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    tableName = 'Volumes'+ '-' +get_account_id()
    table = dynamodb.Table(tableName)
    print(type(table))
    print("not intry " + str(table))
    client = boto3.client('dynamodb', region_name='us-west-2')
    try:
        response = client.describe_table(TableName=tableName)
        print(type(response))
        print("intry " + str(response))
    except ClientError as ce:
        if ce.response['Error']['Code'] == 'ResourceNotFoundException':
            print("Table " + tableName + " does not exist. Let's create a table.")
            print("inexcept")
            table = dynamodb.create_table(
                TableName=tableName,
                KeySchema=[
                    {
                        'AttributeName': 'volume_id',
                        'KeyType': 'HASH'  #Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'volume_id',
                        'AttributeType': 'S'
                    },
                        
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
        else:
            print("Unknown exception occurred while querying for the " + tableName + " table. Printing full error:")
            print(ce.response)    
    print("Table status:", table.table_status)
    print("tablestatus " + str(table.table_status not in ("active")))
    # checking if the table is active status. If not wait for 10 seconds
    try:
        if table.table_status not in ("ACTIVE"):
            #putting wait for 10 seconds to table creation if it does not exists
            t = 10
            time.sleep(t) 
    except ClientError:
        print("Table %s is in status of creating " % table.name)
            
    volumes = event['detail']['requestParameters']['evaluations']
    for volume in volumes:
        #print(volume)
        volume_id = volume['complianceResourceId']
        timestamp = str(datetime.datetime.utcnow())
        #print(type(volume_id))
        #print(type(timestamp))
        print("Adding Volumes:", volume_id, timestamp)
        try:
            table.put_item(
                Item={
                    'volume_id' : volume_id,
                    'timestamp' : timestamp,
                },
                ConditionExpression = 'attribute_not_exists(volume_id)'
            )
        except botocore.exceptions.ClientError as e:
            # Ignore the ConditionalCheckFailedException, bubble up other exceptions.
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise
    
    
       
       