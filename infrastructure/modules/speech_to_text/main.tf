provider "aws" {
    region = var.aws_region
}

# IAM role for Lambda execution
data "aws_iam_policy_document" "assume_role" {
    statement {
        effect = "Allow"

        principals {
            type        = "Service"
            identifiers = ["lambda.amazonaws.com"]
        }

        actions = ["sts:AssumeRole"]
    }
}

resource "aws_iam_role" "lambda_func_iam_role" {
    name               = "${var.lambda_function_name}_${var.environment}_execution_role"
    assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
    role       = aws_iam_role.lambda_func_iam_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_s3_bucket" "lambda_bucket" {
    bucket        = "${lower(var.application_name)}upload-${var.environment}"
    force_destroy = true

    tags = {
        Environment = var.environment
        Application = var.application_name
    }
}

locals {
    test_flac_path = "${path.module}/fixtures/test.flac"
}

resource "aws_s3_object" "test_flac" {
    count = fileexists(local.test_flac_path) ? 1 : 0

    bucket       = aws_s3_bucket.lambda_bucket.id
    key          = "uploads/test.flac"
    source       = local.test_flac_path
    etag         = filemd5(local.test_flac_path)
    content_type = "audio/flac"
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "transcribe_bucket_access" {
    statement {
        sid    = "AllowTranscribePutObject"
        effect = "Allow"

        principals {
            type        = "Service"
            identifiers = ["transcribe.amazonaws.com"]
        }

        actions = ["s3:PutObject"]
        resources = ["${aws_s3_bucket.lambda_bucket.arn}/*"]

        condition {
            test     = "StringEquals"
            variable = "aws:SourceAccount"
            values   = [data.aws_caller_identity.current.account_id]
        }

        condition {
            test     = "ArnLike"
            variable = "aws:SourceArn"
            values   = ["arn:aws:transcribe:${var.aws_region}:${data.aws_caller_identity.current.account_id}:transcription-job/*"]
        }
    }

    statement {
        sid    = "AllowTranscribeGetBucketLocation"
        effect = "Allow"

        principals {
            type        = "Service"
            identifiers = ["transcribe.amazonaws.com"]
        }

        actions   = ["s3:GetBucketLocation", "s3:ListBucket"]
        resources = [aws_s3_bucket.lambda_bucket.arn]

        condition {
            test     = "StringEquals"
            variable = "aws:SourceAccount"
            values   = [data.aws_caller_identity.current.account_id]
        }

        condition {
            test     = "ArnLike"
            variable = "aws:SourceArn"
            values   = ["arn:aws:transcribe:${var.aws_region}:${data.aws_caller_identity.current.account_id}:transcription-job/*"]
        }
    }
}

resource "aws_s3_bucket_policy" "transcribe_bucket_access" {
    bucket = aws_s3_bucket.lambda_bucket.id
    policy = data.aws_iam_policy_document.transcribe_bucket_access.json
}

data "aws_iam_policy_document" "lambda_s3_access" {
    statement {
        effect = "Allow"
        actions = [
            "s3:GetObject",
            "s3:PutObject",
            "s3:DeleteObject"
        ]
        resources = ["${aws_s3_bucket.lambda_bucket.arn}/*"]
    }

    statement {
        effect = "Allow"
        actions = [
            "s3:ListBucket"
        ]
        resources = [aws_s3_bucket.lambda_bucket.arn]
    }
}

resource "aws_iam_role_policy" "lambda_s3_access" {
    name   = "${var.lambda_function_name}_${var.environment}_s3_access"
    role   = aws_iam_role.lambda_func_iam_role.id
    policy = data.aws_iam_policy_document.lambda_s3_access.json
}

data "aws_iam_policy_document" "lambda_transcribe_access" {
    statement {
        effect = "Allow"
        actions = [
            "transcribe:StartTranscriptionJob",
            "transcribe:GetTranscriptionJob",
            "transcribe:ListTranscriptionJobs",
            "transcribe:DeleteTranscriptionJob"
        ]
        resources = [
            "arn:aws:transcribe:${var.aws_region}:*:transcription-job/*"
        ]
    }
}

resource "aws_iam_role_policy" "lambda_transcribe_access" {
    name   = "${var.lambda_function_name}_${var.environment}_transcribe_access"
    role   = aws_iam_role.lambda_func_iam_role.id
    policy = data.aws_iam_policy_document.lambda_transcribe_access.json
}

data "aws_iam_policy_document" "lambda_sqs_access" {
    statement {
        effect = "Allow"
        actions = [
            "sqs:SendMessage"
        ]
        resources = [var.queue_arn]
    }
}

resource "aws_iam_role_policy" "lambda_sqs_access" {
    name   = "${var.lambda_function_name}_${var.environment}_sqs_access"
    role   = aws_iam_role.lambda_func_iam_role.id
    policy = data.aws_iam_policy_document.lambda_sqs_access.json
}

resource "aws_ecr_repository" "ECR" {
  name = "${lower(var.lambda_function_name)}-${var.environment}"
    force_delete = true
}

# Lambda function
resource "aws_lambda_function" "lambda_func" {
    function_name    = "${var.lambda_function_name}_${var.environment}"
    role             = aws_iam_role.lambda_func_iam_role.arn
    package_type     = "Image"
    image_uri        = var.lambda_function_image_uri
    timeout = 60

    environment {
        variables = {
            ENVIRONMENT = var.environment
            LOG_LEVEL   = var.log_level
            S3_BUCKET   = aws_s3_bucket.lambda_bucket.bucket
            SQS_QUEUE_URL = var.queue_url
        }
    }

    tags = {
        Environment = var.environment
        Application = var.application_name
    }
}

# Lambda Function URL (provides HTTP endpoint)
resource "aws_lambda_function_url" "lambda_func_url" {
    function_name      = aws_lambda_function.lambda_func.function_name
    authorization_type = "AWS_IAM"

    cors {
        allow_credentials = false
        allow_origins     = ["*"]
        allow_methods     = ["GET", "POST"]
        allow_headers     = ["*"]
        max_age           = 86400
    }
}
