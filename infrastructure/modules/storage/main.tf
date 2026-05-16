provider "aws" {
    region = var.aws_region
}

resource "aws_dynamodb_table" "response_table" {
    name         = "${lower(var.application_name)}-response-${var.environment}"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "user_name"
    range_key    = "timestamp"

    attribute {
        name = "id"
        type = "S"
    }

    attribute {
        name = "timestamp"
        type = "N"
    }

    tags = {
        Environment = var.environment
        Application = var.application_name
    }
}