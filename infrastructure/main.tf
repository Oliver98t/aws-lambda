module "speech_to_text_lambda_function"  {
  source = "./modules/speechToText"

  aws_region                = var.aws_region
  lambda_function_name      = "speech_to_text"
  lambda_handler            = "Index.handler"
  lambda_source_file        = "${path.module}/../lambda/speechToText/Index.py"
  lambda_requirements_file  = "${path.module}/../lambda/speechToText/requirements.txt"
  lambda_build_dir          = "${path.module}/../lambda/speechToText/build"
  lambda_zip_file           = "${path.module}/../lambda/speechToText/build/zip/package.zip"
  environment               = var.environment
  application_name          = var.application_name
  queue_url                 = module.lambda_queue.queue_url
  queue_arn                 = module.lambda_queue.queue_arn
}

module "lambda_queue"  {
  source = "./modules/queue"

  aws_region                = var.aws_region
  environment               = var.environment
  application_name          = var.application_name
}

module "response_lambda_function"  {
  source = "./modules/response"

  aws_region                = var.aws_region
  lambda_function_name      = "response"
  lambda_handler            = "Index.handler"
  lambda_source_file        = "${path.module}/../lambda/response/Index.py"
  lambda_requirements_file  = "${path.module}/../lambda/response/requirements.txt"
  lambda_build_dir          = "${path.module}/../lambda/response/build"
  lambda_zip_file           = "${path.module}/../lambda/response/build/zip/package.zip"
  environment               = var.environment
  application_name          = var.application_name
  queue_arn                 = module.lambda_queue.queue_arn
}