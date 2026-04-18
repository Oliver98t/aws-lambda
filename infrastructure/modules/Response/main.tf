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

resource "aws_dynamodb_table" "response_table" {
    name         = "${lower(var.application_name)}-response-${var.environment}"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "id"

    attribute {
        name = "id"
        type = "S"
    }

    tags = {
        Environment = var.environment
        Application = var.application_name
    }
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
            "dynamodb:Scan"
        ]
        resources = [aws_dynamodb_table.response_table.arn]
    }
}

resource "aws_iam_role_policy" "lambda_dynamodb_access" {
    name   = "${var.lambda_function_name}_${var.environment}_dynamodb_access"
    role   = aws_iam_role.lambda_func_iam_role.id
    policy = data.aws_iam_policy_document.lambda_dynamodb_access.json
}

resource "aws_ecr_repository" "ECR" {
  name = "${lower(var.lambda_function_name)}-${var.environment}"
}

# Build the Lambda package directory with Python dependencies.
resource "null_resource" "lambda_build" {
    triggers = {
        source_hash       = filebase64sha256(var.lambda_source_file)
        requirements_hash = filebase64sha256(var.lambda_requirements_file)
    }
    
    provisioner "local-exec" {
        command = <<-EOT
            rm -rf "${var.lambda_build_dir}"
            mkdir -p "${var.lambda_build_dir}"
            python3 -m pip install -r "${var.lambda_requirements_file}" -t "${var.lambda_build_dir}"
            cp "${var.lambda_source_file}" "${var.lambda_build_dir}/$(basename "${var.lambda_source_file}")"
        EOT
    }
}

# Package the Lambda function code and installed dependencies.
data "archive_file" "lambda_func_file" {
    type        = "zip"
    source_dir  = "${var.lambda_build_dir}"
    output_path = "${var.lambda_zip_file}"

    depends_on = [null_resource.lambda_build]
}
    
# Lambda function
resource "aws_lambda_function" "lambda_func" {
    filename         = data.archive_file.lambda_func_file.output_path
    function_name    = "${var.lambda_function_name}_${var.environment}"
    role             = aws_iam_role.lambda_func_iam_role.arn
    handler          = var.lambda_handler
    source_code_hash = data.archive_file.lambda_func_file.output_base64sha256

    runtime = var.lambda_runtime
    timeout = 60

    environment {
        variables = {
            ENVIRONMENT = var.environment
            LOCAL_TEST  = var.local_test
            TABLE_NAME  = aws_dynamodb_table.response_table.name
        }
    }
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
    event_source_arn = var.queue_arn
    function_name    = aws_lambda_function.lambda_func.arn
    batch_size       = var.sqs_batch_size
    enabled          = true
}