provider "aws" {
    region = var.aws_region
}

resource "aws_sqs_queue" "lambda_queue" {
    name = "${var.application_name}_${var.environment}_queue"
    visibility_timeout_seconds = 60
}

