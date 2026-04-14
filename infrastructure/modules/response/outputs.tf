# Lambda Function Outputs
output "lambda_function_arn" {
    description = "The ARN of the Lambda function"
    value       = aws_lambda_function.lambda_func.arn
}

output "lambda_function_name" {
    description = "The name of the Lambda function"
    value       = aws_lambda_function.lambda_func.function_name
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

output "dynamodb_table_name" {
    description = "The name of the DynamoDB table used by the response Lambda"
    value       = aws_dynamodb_table.response_table.name
}

output "dynamodb_table_arn" {
    description = "The ARN of the DynamoDB table used by the response Lambda"
    value       = aws_dynamodb_table.response_table.arn
}