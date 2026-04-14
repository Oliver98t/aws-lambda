variable "aws_region" {
    description = "AWS region where resources will be created"
    type        = string
    default     = "eu-west-2"
}

variable "lambda_function_name" {
    description = "Name of the Lambda function"
    type        = string
}

variable "lambda_runtime" {
    description = "Runtime for the Lambda function"
    type        = string
    default     = "python3.12"
}

variable "lambda_handler" {
    description = "Handler for the Lambda function"
    type        = string
    default     = "index.handler"
}

variable "lambda_source_file" {
    description = "Path to the Lambda source code file"
    type        = string
    default     = "lambda/index.py"
}

variable "lambda_requirements_file" {
    description = "Path to the Lambda requirements file"
    type        = string
    default     = "lambda/requirements.txt"
}

variable "lambda_build_dir" {
    description = "Path to the temporary Lambda build directory"
    type        = string
    default     = "lambda/build"
}

variable "lambda_zip_file" {
    description = "Path to the Lambda ZIP file"
    type        = string
    default     = "lambda/function.zip"
}

variable "environment" {
    description = "Environment name (e.g., production, staging, development)"
    type        = string
}

variable "log_level" {
    description = "Log level for the Lambda function"
    type        = string
    default     = "info"
}

variable "local_test" {
    description = "environment variable for local testing"
    type        = string
    default     = "LOCAL_TEST"
}

variable "application_name" {
    description = "Name of the application"
    type        = string
}

variable "queue_arn" {
    description = "ARN of the SQS queue that triggers this Lambda"
    type        = string
}

variable "sqs_batch_size" {
    description = "Number of messages to process per Lambda invocation"
    type        = number
    default     = 10
}