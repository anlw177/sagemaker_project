resource "aws_s3_object" "test_deploy_script_s3" {
  bucket = var.s3_bucket
  key = "glue/scripts/TestDeployScript.py"
  source = "${local.glue_src_path}TestDeployScript.py"
  etag = filemd5("${local.glue_src_path}TestDeployScript.py")
}

resource "aws_glue_job" "test_deploy_script" {
  glue_version = "4.0" #optional
  max_retries = 0 #optional
  name = "TestDeployScript" #required
  description = "test the deployment of an aws glue job to aws glue service with terraform" #description
  role_arn = aws_iam_role.glue_service_role.arn #required
  number_of_workers = 2 #optional, defaults to 5 if not set
  worker_type = "G.1X" #optional
  timeout = "60" #optional
  execution_class = "FLEX" #optional
  tags = {
    project = var.project #optional
  }
  command {
    name="glueetl" #optional
    script_location = "s3://${var.s3_bucket}/glue/scripts/TestDeployScript.py" #required
  }
  default_arguments = {
    "--class"                   = "GlueApp"
    "--enable-job-insights"     = "true"
    "--enable-auto-scaling"     = "false"
    "--enable-glue-datacatalog" = "true"
    "--job-language"            = "python"
    "--job-bookmark-option"     = "job-bookmark-disable"
    "--datalake-formats"        = "iceberg"
    "--conf"                    = "spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions  --conf spark.sql.catalog.glue_catalog=org.apache.iceberg.spark.SparkCatalog  --conf spark.sql.catalog.glue_catalog.warehouse=s3://tnt-erp-sql/ --conf spark.sql.catalog.glue_catalog.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog  --conf spark.sql.catalog.glue_catalog.io-impl=org.apache.iceberg.aws.s3.S3FileIO"

  }
}


resource "aws_glue_job" "data_cleaning_job" {
  name         = "data-cleaning-job"
  role_arn     = aws_iam_role.glue_service_role.arn
  glue_version = "4.0"
  worker_type  = "G.1X"
  number_of_workers = 2

  command {
    script_location = "s3://${var.s3_bucket}/scripts/clean_data.py"
    python_version  = "3"
  }
}


resource "aws_glue_job" "data_aggregation_job" {
  name         = "data-aggregation-job"
  role_arn     = aws_iam_role.glue_service_role.arn
  glue_version = "4.0"
  worker_type  = "G.1X"
  number_of_workers = 2

  command {
    script_location = "s3://${var.s3_bucket}/scripts/aggregate_data.py"
    python_version  = "3"
  }
}



resource "aws_glue_trigger" "job_trigger" {
  name = "trigger-job2-after-job1"
  type = "CONDITIONAL"

  actions {
    job_name = aws_glue_job.data_aggregation_job.name
  }

  predicate {
    conditions {
      job_name = aws_glue_job.data_cleaning_job.name
      state    = "SUCCEEDED"
    }
  }
}

resource "aws_glue_job" "sagemaker_trigger_job" {
  name          = "sagemaker-trigger-job"
  role_arn      = aws_iam_role.glue_service_role.arn
  glue_version  = "4.0"
  worker_type   = "G.1X"
  number_of_workers = 2
  
  command {
    script_location = "s3://${var.s3_bucket}/scripts/trigger_sagemaker_job.py"
    python_version  = "3"
  }
}