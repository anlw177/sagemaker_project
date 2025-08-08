terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.30.0"  # Replace with your desired version constraint
    }

    }
  }

  provider "aws" {
    region = "us-east-1"  # Set your desired AWS region
    profile = "default"
}

terraform {
  backend "s3" {
    bucket = "lookuptestbucket"
    key    = "terraform/terraform.tfstate"
    region = "us-east-1"
    profile = "default"
  }
}