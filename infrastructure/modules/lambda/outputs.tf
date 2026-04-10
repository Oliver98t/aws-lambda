# Lambda Function Outputs
output "lambda_function_arn" {
    description = "The ARN of the Lambda function"
    value       = aws_lambda_function.lambda_func.arn
}

output "lambda_function_name" {
    description = "The name of the Lambda function"
    value       = aws_lambda_function.lambda_func.function_name
}

output "lambda_function_invoke_arn" {
    description = "The invoke ARN of the Lambda function"
    value       = aws_lambda_function.lambda_func.invoke_arn
}

output "lambda_function_version" {
    description = "Latest published version of the Lambda function"
    value       = aws_lambda_function.lambda_func.version
}

output "lambda_function_qualified_arn" {
    description = "The qualified ARN of the Lambda function"
    value       = aws_lambda_function.lambda_func.qualified_arn
}

# IAM Role Outputs
output "lambda_role_arn" {
    description = "The ARN of the Lambda execution IAM role"
    value       = aws_iam_role.lambda_func_iam_role.arn
}

output "lambda_role_name" {
    description = "The name of the Lambda execution IAM role"
    value       = aws_iam_role.lambda_func_iam_role.name
}

# Source Code Hash Output
output "lambda_source_code_hash" {
    description = "Base64-encoded SHA256 hash of the Lambda deployment package"
    value       = aws_lambda_function.lambda_func.source_code_hash
}

# Lambda Function URL Output
output "lambda_function_url" {
    description = "The HTTP(S) URL endpoint for the Lambda function"
    value       = aws_lambda_function_url.lambda_func_url.function_url
}
