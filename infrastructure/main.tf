module "speech_to_text_lambda_function"  {
  source = "./modules/SpeechToText"

  aws_region                = var.aws_region
  lambda_function_name      = "SpeechToText"
  environment               = var.environment
  application_name          = var.application_name
  lambda_function_image_uri = var.SpeechToText_image_uri
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
  environment               = var.environment
  application_name          = var.application_name
  lambda_function_image_uri = var.Response_image_uri
  queue_arn                 = module.lambda_queue.queue_arn
}