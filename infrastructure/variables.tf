variable "aws_region" {
	description = "AWS region where resources will be created"
	type        = string
	default     = "eu-west-2"
}

variable "application_name" {
	description = "Name of the application"
	type        = string
	default     = "AInterview"
}

variable "environment" {
	description = "Environment name (e.g., production, staging, development)"
	type        = string
}

variable "Response_image_uri" {
	description = "Name of the application"
	type        = string
}

variable "SpeechToText_image_uri" {
	description = "Name of the application"
	type        = string
}