module "speech_to_text_lambda_function"  {
  source = "./modules/SpeechToText"

  aws_region                = var.aws_region
  lambda_function_name      = "SpeechToText"
  lambda_handler            = "Index.handler"
  lambda_source_file        = "${path.module}/../LambdaSrc/SpeechToText/Index.py"
  lambda_requirements_file  = "${path.module}/../LambdaSrc/SpeechToText/requirements.txt"
  lambda_build_dir          = "${path.module}/../LambdaSrc/SpeechToText/build"
  lambda_zip_file           = "${path.module}/../LambdaSrc/SpeechToText/build/zip/package.zip"
  environment               = var.environment
  application_name          = var.application_name
  queue_url                 = module.lambda_queue.queue_url
  queue_arn                 = module.lambda_queue.queue_arn
}

module "lambda_queue"  {
  source = "./modules/Queue"

  aws_region                = var.aws_region
  environment               = var.environment
  application_name          = var.application_name
}

module "response_lambda_function"  {
  source = "./modules/Response"

  aws_region                = var.aws_region
  lambda_function_name      = "Response"
  lambda_handler            = "Index.handler"
  lambda_source_file        = "${path.module}/../LambdaSrc/Response/Index.py"
  lambda_requirements_file  = "${path.module}/../LambdaSrc/Response/requirements.txt"
  lambda_build_dir          = "${path.module}/../LambdaSrc/Response/build"
  lambda_zip_file           = "${path.module}/../LambdaSrc/Response/build/zip/package.zip"
  environment               = var.environment
  application_name          = var.application_name
  queue_arn                 = module.lambda_queue.queue_arn
}