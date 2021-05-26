#!/usr/bin/python

import sys, getopt
import os
import boto3
from time import sleep


buffer_size = 1024*100000

source_region_name = os.getenv('AWS_DEFAULT_REGION')
source_aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
source_aws_secret_access_key = os.getenv('AWS_SECRET_KEY')
source_bucket = os.getenv('AWS_S3_BUCKET_SOURCE')

target_region_name = os.getenv('AWS_GOV_DEFAULT_REGION')
target_aws_access_key_id = os.getenv('AWS_GOV_ACCESS_KEY')
target_aws_secret_access_key = os.getenv('AWS_GOV_SECRET_KEY')
target_bucket = os.getenv('AWS_GOV_S3_BUCKET_TARGET')

def aws_transfer_s3_object_to_gov(
  sourceS3ObjectKey,
  sourceBucket,
  targetS3ObjectKey,
  targetBucket):

  source_s3 =boto3.client(
    's3',
    region_name=source_region_name,
    aws_access_key_id=source_aws_access_key_id, 
    aws_secret_access_key=source_aws_secret_access_key
  )

  target_s3 =boto3.client(
    's3',
    region_name=target_region_name,
    aws_access_key_id=target_aws_access_key_id,
    aws_secret_access_key=target_aws_secret_access_key
  )

  s3_obj = source_s3.get_object(Bucket=sourceBucket, Key=sourceS3ObjectKey)
  body = s3_obj['Body']

  mpu = target_s3.create_multipart_upload(Bucket=targetBucket, Key=targetS3ObjectKey)
  mpu_id = mpu["UploadId"]

  parts = []
  uploaded_bytes = 0
  part_index = 1

  while (True):
      chunk = body.read(buffer_size)
      if chunk == b'':
          break
      part = target_s3.upload_part(
          Body=chunk,
          Bucket=targetBucket,
          Key=targetS3ObjectKey,
          UploadId=mpu_id,
          PartNumber=part_index
      )
      parts.append({"PartNumber": part_index, "ETag": part["ETag"]})
      uploaded_bytes += len(chunk)
      part_index += 1

  part_info = {'Parts': parts}


  target_s3.complete_multipart_upload(
      Bucket=targetBucket,
      Key=targetS3ObjectKey,
      UploadId=mpu_id,
      MultipartUpload=part_info
  )

  return 0

def aws_export_ami_to_s3(
  sourceImageId,
  sourceImageName,
  sourceImageReleaseType,
  targetBucket):

  source_ec2 =boto3.client(
    'ec2',
    region_name=source_region_name,
    aws_access_key_id=source_aws_access_key_id,
    aws_secret_access_key=source_aws_secret_access_key
  )

  response = source_ec2.create_store_image_task(
      ImageId=sourceImageId,
      Bucket=targetBucket
  )
  imageS3FileName = response['ObjectKey']

  # check for status until finished:
  while (True):
    sleep(5)
    response = source_ec2.describe_store_image_tasks(
      ImageIds=[
          sourceImageId,
      ]
    )
    status = response['StoreImageTaskResults'][0]
    if status['StoreTaskState'] == 'Completed':
      break;

  return imageS3FileName

def aws_restore_ami_from_s3(
  sourceBucket,
  sourceImageS3Key,
  sourceImageName):

  source_ec2 =boto3.client(
    'ec2',
    region_name=target_region_name,
    aws_access_key_id=target_aws_access_key_id,
    aws_secret_access_key=target_aws_secret_access_key
  )

  response = source_ec2.create_restore_image_task(
    Bucket=sourceBucket,
    ObjectKey=sourceImageS3Key,
    Name=sourceImageName
  )

  imageId = response['ImageId']

  return imageId

def main():
  sourceImageId = ''
  sourceImageName = ''
  argv = sys.argv[1:]
  
  opts = []
  args = []
  try:
    opts, args = getopt.getopt(argv,"hi:n:",["ami=","name="])
  except getopt.GetoptError:
    print('ami_copy_2_gov.py -i <AMI ID> -n <AMI Name>')
    sys.exit(2)
  if not opts:
    print('ami_copy_2_gov.py -i <AMI ID> -n <AMI Name>')
    sys.exit() 
    
  for opt, arg in opts:
    if opt == '-h':
      print('ami_copy_2_gov.py -i <AMI ID> -n <AMI Name>')
      sys.exit()
    elif opt in ("-i", "--ami"):
      sourceImageId = arg
    elif opt in ("-n", "--name"):
      sourceImageName = arg
  
  print('Copy AWS AMI from Commercial cloud to government cloud:')
  print('Source AMI ID: ' + sourceImageId)
  print('Source AMI Name: '+ sourceImageName)
  
  # First we need to export the AMI to a S3 object:
  amiS3ObjectKey = aws_export_ami_to_s3(
    sourceImageId=sourceImageId,
    sourceImageName=sourceImageName,
    sourceImageReleaseType='GA',
    targetBucket=source_bucket
  )

  print('AMI Exported to S3 Object: ' + amiS3ObjectKey + ' in ' + source_bucket + ' bucket.')

  # copy the exported AMI to Gov Account:
  aws_transfer_s3_object_to_gov(
    sourceS3ObjectKey=amiS3ObjectKey,
    sourceBucket=source_bucket,
    targetS3ObjectKey=amiS3ObjectKey,
    targetBucket=target_bucket
  )

  print('AMI replicated to government cloud S3 Object: ' + amiS3ObjectKey + ' in ' + target_bucket + ' bucket.')

  # Finally Restore the Image on Gov cloud:
  gov_ami_id = aws_restore_ami_from_s3(
    sourceBucket=target_bucket,
    sourceImageS3Key=amiS3ObjectKey,
    sourceImageName=sourceImageName
  )

  print('New Gov Cloud AMI Created: ' + gov_ami_id)
  
  return 0

if __name__ == "__main__":
    main()
