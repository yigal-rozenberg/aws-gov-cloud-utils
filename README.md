# aws-gov-cloud-utils
Helper Python Scripts to transfer content between commercial and government cloud partitions.

The implmentation is based on a new aws api functionality that allows storing AMI in a single S3 blob, and restoring the AMI from the blob.

The source AMI is serialize to a S3 blob by calling the boto3 create_store_image_task() function.
The blob then transfered from commercial cloud to goverement cloud using buffered download and upload instead of downloading and uploading the whle blob to the machine where the script is executed.
Once the blbo replicated to a goverment cloud S3 bucket, it is restored by calling boto3 create_restore_image_task() function.

The describe_store_image_tasks() function is used to check completion of the export task.
There is no equivalent API for restore image tasks.

1. reference: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html
2. create_store_image_task() https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.create_store_image_task
3. create_restore_image_task() https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.create_restore_image_task
4. describe_store_image_tasks() https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_store_image_tasks
