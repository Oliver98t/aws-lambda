module "speech_to_text_lambda_function"  {
  source = "./modules/speech_to_text"

  aws_region                = var.aws_region
  lambda_function_name      = "speech_to_text"
  environment               = var.environment
  application_name          = var.application_name
  lambda_function_image_uri = var.speech_to_text_image_uri
  queue_url                 = module.lambda_queue.queue_url
  queue_arn                 = module.lambda_queue.queue_arn
  local_test                = var.local_test
}

module "lambda_queue"  {
  source = "./modules/queue"

  aws_region                = var.aws_region
  environment               = var.environment
  application_name          = var.application_name
}

module "storage" {
    source = "./modules/storage"
    aws_region = var.aws_region
    environment = var.environment
    application_name = var.application_name
}

module "response_lambda_function"  {
  source = "./modules/response"

  aws_region                = var.aws_region
  lambda_function_name      = "response"
  environment               = var.environment
  application_name          = var.application_name
  lambda_function_image_uri = var.response_image_uri
  queue_arn                 = module.lambda_queue.queue_arn
  dynamodb_table_arn        = module.storage.dynamodb_table_arn
  dynamodb_table_name       = module.storage.dynamodb_table_name
  local_test                = var.local_test
}

module "get_response_lambda_function" {
    source = "./modules/get_response"

    aws_region                  = var.aws_region
    lambda_function_name        = "get_response"
    environment                 = var.environment
    application_name            = var.application_name
    lambda_function_image_uri   = var.get_response_image_uri
    dynamodb_table_arn          = module.storage.dynamodb_table_arn
    dynamodb_table_name         = module.storage.dynamodb_table_name
    local_test                  = var.local_test
}