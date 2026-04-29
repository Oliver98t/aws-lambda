provider "aws" {
  region = var.aws_region
}

locals {
  lambda_function_name = "${var.lambda_function_name}_${var.environment}"
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

# DynamoDB read-only access policy
data "aws_iam_policy_document" "lambda_dynamodb_access" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:Query",
      "dynamodb:Scan"
    ]
    resources = [var.dynamodb_table_arn]
  }
}

resource "aws_ecr_repository" "ECR" {
    name = local.lambda_function_name
    force_delete = true
}

resource "aws_iam_role_policy" "lambda_dynamodb_access" {
  name   = "${var.lambda_function_name}_${var.environment}_dynamodb_access"
  role   = aws_iam_role.lambda_func_iam_role.id
  policy = data.aws_iam_policy_document.lambda_dynamodb_access.json
}

resource "aws_lambda_function" "lambda_func" {
  function_name = local.lambda_function_name
  role          = aws_iam_role.lambda_func_iam_role.arn
  package_type  = "Image"
  image_uri     = var.lambda_function_image_uri
  timeout       = 60

  environment {
    variables = {
      ENVIRONMENT     = var.environment
      LOG_LEVEL       = var.log_level
      DYNAMODB_TABLE  = var.dynamodb_table_name
      LOCAL_TEST      = var.local_test
    }
  }

  tags = {
    Environment = var.environment
    Application = var.application_name
  }
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

# CloudWatch log group for Lambda
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.lambda_func.function_name}"
  retention_in_days = 14
}