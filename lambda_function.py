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
