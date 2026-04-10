module "speech_to_text_lambda_function"  {
  source = "./modules/lambda"

  aws_region           = var.aws_region
  lambda_function_name = "speech_to_text"
  lambda_handler       = "index.handler"
  lambda_source_file   = "${path.module}/../lambda/index1.py"
  lambda_zip_file      = "${path.module}/../lambda/function.zip"
  environment          = var.environment
  application_name     = var.application_name
}

module "response_lambda_function"  {
  source = "./modules/lambda"

  aws_region           = var.aws_region
  lambda_function_name = "response"
  lambda_handler       = "index.handler"
  lambda_source_file   = "${path.module}/../lambda/index2.py"
  lambda_zip_file      = "${path.module}/../lambda/function.zip"
  environment          = var.environment
  application_name     = var.application_name
}