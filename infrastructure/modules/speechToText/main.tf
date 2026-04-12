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
    name               = "${var.lambda_function_name}_execution_role"
    assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
    role       = aws_iam_role.lambda_func_iam_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
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

    environment {
        variables = {
            ENVIRONMENT = var.environment
            LOG_LEVEL   = var.log_level
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