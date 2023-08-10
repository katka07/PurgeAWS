import boto3
from botocore.exceptions import NoCredentialsError
from django.shortcuts import render, redirect
from .models import AWSUser, Resource
import logging
logging.getLogger('botocore').setLevel(logging.DEBUG)

# ==========================================================================================

def home(request):
    error_message = ""
    if request.method == 'POST':
        access_key = request.POST.get('access_key')
        secret_key = request.POST.get('secret_key')        
        try:
            # Validate credentials by listing S3 buckets
            s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name='us-east-1')
            buckets = s3_client.list_buckets()
            
            if not buckets:
                error_message = "Invalid AWS credentials."
            else:
                request.session['access_key'] = access_key  # Store access key in session
                request.session['secret_key'] = secret_key  # Store secret key in session
                return redirect('options')
        except NoCredentialsError as e:
            print(e)
            error_message = "Invalid AWS credentials."
            
    return render(request, 'home.html', {'error_message': error_message})

# ==========================================================================================

def options(request):
    return render(request, 'options.html')

# ==========================================================================================

def list_resources(request):
    access_key = request.session.get('access_key')  # Retrieve access key from session
    secret_key = request.session.get('secret_key')  # Retrieve secret key from session

    try:
        resources = get_resources_list(access_key, secret_key)
        if resources:
            return render(request, 'list_resources.html', {'resources': resources})
        else:
            no_resources_message = "No running resources found."
            return render(request, 'list_resources.html', {'no_resources_message': no_resources_message})
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return render(request, 'list_resources.html', {'error_message': error_message})


# ==========================================================================================

def get_resources_list(access_key, secret_key):
    s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    ec2_client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    rds_client = boto3.client('rds', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    ec2_resource = boto3.resource('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    resources = []

    # Fetch EC2 instances
    ec2_instances = ec2_client.describe_instances()
    for reservation in ec2_instances['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] == 'running':
                resources.append({'service': 'EC2', 'name': instance['InstanceId']})
    
    # Fetch Security Groups
    security_groups = ec2_client.describe_security_groups()
    for group in security_groups['SecurityGroups']:
            if group['GroupName'] != 'default':
                resources.append({'service': 'SecurityGroup', 'name': group['GroupName']})

    # Fetch S3 buckets
    s3_buckets = s3_client.list_buckets()
    for bucket in s3_buckets['Buckets']:
        resources.append({'service': 'S3', 'name': bucket['Name']})

    # Fetch RDS instances
    rds_instances = rds_client.describe_db_instances()
    for instance in rds_instances['DBInstances']:
        resources.append({'service': 'RDS', 'name': instance['DBInstanceIdentifier']})

    # Fetch VPCs
    vpcs = ec2_resource.vpcs.filter(Filters=[{'Name': 'isDefault', 'Values': ['false']}])
    for vpc in vpcs:
        resources.append({'service': 'VPC', 'name': vpc.id})

    return resources

def delete_resources(request):
    if request.method == 'POST':
        selected_resources = request.POST.getlist('selected_resources')
        access_key = request.session.get('access_key')  # Retrieve access key from session
        secret_key = request.session.get('secret_key')  # Retrieve secret key from session

        try:
            # Delete selected resources based on their type and name
            for resource in selected_resources:
                service, name = resource.split(':')
                if service == 'EC2':
                    ec2_client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                    ec2_client.terminate_instances(InstanceIds=[name])
                elif service == 'S3':
                    s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                    s3_client.delete_bucket(Bucket=name)
                elif service == 'RDS':
                    rds_client = boto3.client('rds', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                    rds_client.delete_db_instance(DBInstanceIdentifier=name, SkipFinalSnapshot=True)
                elif service == 'VPC':
                    ec2_resource = boto3.resource('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                    vpc = ec2_resource.Vpc(id=name)
                    vpc.delete()
                elif service == 'SecurityGroup':
                    ec2_client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                    ec2_client.delete_security_group(GroupName=name)
                    
            return redirect('options') # previously list_resources
        except Exception as e:
            error_message = f"Error: {str(e)}"
            resources = get_resources_list(access_key, secret_key)
            return render(request, 'delete_resources.html', {'resources': resources, 'error_message': error_message})

    resources = get_resources_list(request.session.get('access_key'), request.session.get('secret_key'))
    return render(request, 'delete_resources.html', {'resources': resources})

# ==========================================================================================

