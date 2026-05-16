provider "aws" {
    region = var.aws_region
}

data "aws_caller_identity" "current" {}

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

data "aws_iam_policy_document" "lambda_sqs_consume_access" {
    statement {
        effect = "Allow"
        actions = [
            "sqs:ReceiveMessage",
            "sqs:DeleteMessage",
            "sqs:GetQueueAttributes",
            "sqs:ChangeMessageVisibility"
        ]
        resources = [var.queue_arn]
    }
}

resource "aws_iam_role_policy" "lambda_sqs_consume_access" {
    name   = "${var.lambda_function_name}_${var.environment}_sqs_consume_access"
    role   = aws_iam_role.lambda_func_iam_role.id
    policy = data.aws_iam_policy_document.lambda_sqs_consume_access.json
}

data "aws_iam_policy_document" "lambda_bedrock_access" {
    statement {
        effect = "Allow"
        actions = [
            "bedrock:InvokeModel",
            "bedrock:InvokeModelWithResponseStream"
        ]
        resources = [
            "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:inference-profile/global.amazon.nova-2-lite-v1:0",
            "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.nova-2-lite-v1:0",
            "arn:aws:bedrock:::foundation-model/amazon.nova-2-lite-v1:0"
        ]
    }
}

resource "aws_iam_role_policy" "lambda_bedrock_access" {
    name   = "${var.lambda_function_name}_${var.environment}_bedrock_access"
    role   = aws_iam_role.lambda_func_iam_role.id
    policy = data.aws_iam_policy_document.lambda_bedrock_access.json
}

data "aws_iam_policy_document" "lambda_dynamodb_access" {
    statement {
        effect = "Allow"
        actions = [
            "dynamodb:PutItem",
            "dynamodb:GetItem",
            "dynamodb:UpdateItem",
            "dynamodb:DeleteItem",
            "dynamodb:Query",
            "dynamodb:Scan",
            "dynamodb:BatchWriteItem"
        ]
        resources = [var.dynamodb_table_arn]
    }
}

resource "aws_iam_role_policy" "lambda_dynamodb_access" {
    name   = "${var.lambda_function_name}_${var.environment}_dynamodb_access"
    role   = aws_iam_role.lambda_func_iam_role.id
    policy = data.aws_iam_policy_document.lambda_dynamodb_access.json
}

resource "aws_ecr_repository" "ECR" {
  name = "${lower(var.lambda_function_name)}_${var.environment}"
    force_delete = true
}

# Lambda function
resource "aws_lambda_function" "lambda_func" {
    function_name    = "${var.lambda_function_name}_${var.environment}"
    package_type     = "Image"
    image_uri        = var.lambda_function_image_uri
    role             = aws_iam_role.lambda_func_iam_role.arn
    timeout = 60

    environment {
        variables = {
            ENVIRONMENT = var.environment
            LOCAL_TEST  = var.local_test
            TABLE_NAME  = var.dynamodb_table_name
        }
    }
}

# CloudWatch log group for Lambda
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.lambda_func.function_name}"
  retention_in_days = 14
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
    event_source_arn = var.queue_arn
    function_name    = aws_lambda_function.lambda_func.arn
    batch_size       = var.sqs_batch_size
    enabled          = true
}

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