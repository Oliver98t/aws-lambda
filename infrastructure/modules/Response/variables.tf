variable "aws_region" {
    description = "AWS region where resources will be created"
    type        = string
    default     = "eu-west-2"
}

variable "lambda_function_name" {
    description = "Name of the Lambda function"
    type        = string
}

variable "lambda_function_image_uri" {
    description = "Name of the Lambda function"
    type        = string
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