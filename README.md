# Creating a Lambda Function Using Boto3 to check for tags in EC2 Instances
### Step 1: Create a Role in IAM using AWS management Console

Give these permissions
* AmazonEC2FullAccess
* AmazonSNSFullAccess

### Step 2: In CloudWatch navigate to 'Rules'
Select: 
* Service Name: EC2
* Event Type: EC2 Instance State-change Notification
* Specific Instance -> running

Make Note of the Sample event json file
````
{
  "version": "0",
  "id": "ee376907-2647-4179-9203-343cfb3017a4",
  "detail-type": "EC2 Instance State-change Notification",
  "source": "aws.ec2",
  "account": "123456789012",
  "time": "2015-11-11T21:30:34Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:ec2:us-east-1:123456789012:instance/i-abcd1111"
  ],
  "detail": {
    "instance-id": "i-abcd1111",
    "state": "running"
  }
}
````

### Step 3: Create a file named 'lambda_function.py' in VS Code 
````
import json
import boto3

ec2client = boto3.client('ec2')
snsclient = boto3.client('sns')

def lambda_handler(event, context):
    # TODO implement
    ec2_instance_id=event['detail']['instance-id']
    
    tag_response = ec2client.describe_tags(
        Filters=[
            {
                'Name': 'resource-id',
                'Values': [ec2_instance_id]
            }
        ]
    )
    
    print(tag_response) 
    alltags=tag_response['Tags']
    flag='STOP'
    for item in alltags:
        print(item['Key'])
        if item['Key']=='SPECIAL_EXCEPTION':
            flag='DONT_STOP'
            break
    print(flag)
    
    
    #Decision Making
    if flag=='STOP':
        #STOP EC2
        response = ec2client.stop_instances(InstanceIds=[ec2_instance_id])
        
        #Send mail
        snsarn='arn:aws:sns:us-west-2:466644029397:BadImageSNSTopic'
        errormssg= "EC2"+ ec2_instance_id + " Stopped"
        snsresponse = snsclient.publish(TopicArn=snsarn,
                                    Message=errormssg,
                                    Subject='EC2 Violated!!'
                                    )
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
````

### Step 4: Go in to AWS Management Consolse and choose "Lambda"
##### Create a new function and upload this file "lambda_function.py" as a zip file
##### Click on "Configure test event" and create a template and event named "test1" and copy the json file which we got from cloudwatch and click save
##### Click Test to see everything is working fine
Output:
````
Response
{
  "statusCode": 200,
  "body": "\"Hello from Lambda!\""
}
````

### Step 5: Configure SNS from AWS Management Console
##### Create topic 
##### Create a Subscription
* Choose Protocol as "Email"
* Give your email at the Endpoint

### Step 6: Go into CloudWatch and Click on Rules 
 Select: 
* Service Name: EC2
* Event Type: EC2 Instance State-change Notification
* Specific Instance -> running
* Click on "Add Targets" -> Select lambda function you created earlier
* Click on Configure Details and create