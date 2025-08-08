#/**

resource "aws_sagemaker_model" "model" {
  name = "my-model"
  execution_role_arn = "arn:aws:iam::910326982948:role/SageMakerExecutionRole"

  primary_container {
    image = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3"

    model_data_url = "https://lookuptestbucket.s3.us-east-1.amazonaws.com/deployedModels/model.tar.gz"
  }
}
resource "aws_sagemaker_endpoint_configuration" "endpoint_config" {
  name = "my-endpoint-config"

  production_variants {
    variant_name = "variant-1"
    model_name = aws_sagemaker_model.model.name
    initial_instance_count = 1
    instance_type = "ml.t2.medium"
  }
}

resource "aws_sagemaker_endpoint" "endpoint" {
  name = "my-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.endpoint_config.name
}

#**/