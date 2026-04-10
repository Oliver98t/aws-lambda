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

variable "application_name" {
    description = "Name of the application"
    type        = string
}
