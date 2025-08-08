import boto3
import time
import os

# --- Configuration ---
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "lookuptestbucket" 
SAGEMAKER_ROLE_ARN = "arn:aws:iam::910326982948:role/SageMakerExecutionRole" 
TRAINING_JOB_NAME = f"my-model-training-job-{int(time.time())}" # Unique job name
IMAGE_URI = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3"
INSTANCE_TYPE = "ml.m5.large"
INSTANCE_COUNT = 1
VOLUME_SIZE_IN_GB = 10


TRAINING_DATA_S3_URI = f"s3://{S3_BUCKET_NAME}/processed-data" 
OUTPUT_DATA_S3_URI = f"s3://{S3_BUCKET_NAME}/model-artifacts/"
SCRIPT_S3_URI = f"s3://{S3_BUCKET_NAME}/scripts/train.tar.gz"

# --- Boto3 Client ---
sagemaker_client = boto3.client('sagemaker', region_name=AWS_REGION)

print(f"Starting SageMaker Training Job: {TRAINING_JOB_NAME}")

try:
    response = sagemaker_client.create_training_job(
        TrainingJobName=TRAINING_JOB_NAME,
        HyperParameters={
            "sagemaker_program": "train.py",
            "sagemaker_submit_directory": SCRIPT_S3_URI
        },
        AlgorithmSpecification={
            "TrainingImage": IMAGE_URI,
            "TrainingInputMode": "File"
        },
        RoleArn=SAGEMAKER_ROLE_ARN,
        InputDataConfig=[
            {
                "ChannelName": "training",
                "DataSource": {
                    "S3DataSource": {
                        "S3Uri": TRAINING_DATA_S3_URI,
                        "S3DataType": "S3Prefix",
                        "S3DataDistributionType": "FullyReplicated"
                    }
                },
                # --- Updated ContentType to reflect Parquet data ---
                "ContentType": "application/x-parquet"
            }
        ],
        OutputDataConfig={
            "S3OutputPath": OUTPUT_DATA_S3_URI
        },
        ResourceConfig={
            "InstanceType": INSTANCE_TYPE,
            "InstanceCount": INSTANCE_COUNT,
            "VolumeSizeInGB": VOLUME_SIZE_IN_GB
        },
        StoppingCondition={
            "MaxRuntimeInSeconds": 3600
        }
    )

    print("Training job created successfully!")
    print(f"Response: {response}")

    print("Waiting for training job to complete...")
    sagemaker_client.get_waiter('training_job_completed_or_stopped').wait(
        TrainingJobName=TRAINING_JOB_NAME
    )
    print("Training job finished.")

    description = sagemaker_client.describe_training_job(TrainingJobName=TRAINING_JOB_NAME)
    status = description['TrainingJobStatus']
    print(f"Training Job Status: {status}")

    if status == 'Completed':
        model_artifact_s3_uri = description['OutputDataConfig']['S3OutputLocation']
        print(f"Model artifact available at: {model_artifact_s3_uri}")
    else:
        print(f"Training job failed or was stopped. Reason: {description.get('FailureReason', 'N/A')}")

except Exception as e:
    print(f"Error creating or waiting for training job: {e}")