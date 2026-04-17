terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }
  }
  required_version = ">= 1.2"
  # values loaded in using backend.config
  backend "s3" {
    bucket         = ""
    key            = ""
    region         = ""
    encrypt        = true
  }
}
