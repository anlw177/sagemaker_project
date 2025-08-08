import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import window, avg, col, to_timestamp

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Read cleaned data from S3
cleaned_data_path = "s3://lookuptestbucket/cleaned-data/"
cleaned_df = spark.read.parquet(cleaned_data_path)

# Ensure timestamp is in the correct format for windowing
cleaned_df = cleaned_df.withColumn("timestamp", to_timestamp(col("timestamp")))

# Aggregate data in 5-minute windows
windowed_df = cleaned_df.groupBy(
    window(col("timestamp"), "5 minutes")
).agg(
    avg("temperature").alias("avg_temperature"),
    avg("humidity").alias("avg_humidity")
)

# Write aggregated data to S3
output_path = "s3://lookuptestbucket/processed-data/"
windowed_df.write.format("parquet").mode("overwrite").save(output_path)
