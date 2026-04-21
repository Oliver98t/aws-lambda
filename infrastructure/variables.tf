variable "application_name" {
	description = "Name of the application"
	type        = string
	default     = "AInterview"
}

variable "aws_region" {
	description = "AWS region where resources will be created"
	type        = string

}

variable "environment" {
	description = "Environment name (e.g., production, staging, development)"
	type        = string
}

variable "response_image_uri" {
	description = "Name of the application"
	type        = string
}

variable "speech_to_text_image_uri" {
	description = "Name of the application"
	type        = string
}