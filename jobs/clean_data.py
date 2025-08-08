import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read raw data from S3
source_path = "s3://lookuptestbucket/raw-data/"
raw_dynamic_frame = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [source_path]},
    format="json"
)

# Convert to DataFrame for easier manipulation
raw_df = raw_dynamic_frame.toDF()

# Simple cleaning: add a new column for example
cleaned_df = raw_df.withColumn("data_source", col("timestamp"))

# Write the cleaned data to S3
output_path = "s3://lookuptestbucket/cleaned-data/"
cleaned_dynamic_frame = DynamicFrame.fromDF(cleaned_df, glueContext, "cleaned_df")
glueContext.write_dynamic_frame.from_options(
    frame=cleaned_dynamic_frame,
    connection_type="s3",
    connection_options={"path": output_path},
    format="parquet"
)

job.commit()
