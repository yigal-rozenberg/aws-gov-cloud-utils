# aws-gov-cloud-utils
Helper Python Scripts to transfer content between commercial and government cloud partitions.

The implmentation is based on a new aws api functionality that allows storing AMI in a single S3 blob, and restoring the AMI from the blob.

1. reference: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html
2. create_store_image_task() https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.create_store_image_task
3. create_restore_image_task() https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.create_restore_image_task
4. describe_store_image_tasks() https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_store_image_tasks
