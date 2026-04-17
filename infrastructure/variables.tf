variable "aws_region" {
	description = "AWS region where resources will be created"
	type        = string
	default     = "eu-west-2"
}

variable "environment" {
	description = "Environment name (e.g., production, staging, development)"
	type        = string
}

variable "application_name" {
	description = "Name of the application"
	type        = string
	default     = "AInterview"
}
