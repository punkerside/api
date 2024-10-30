resource "aws_dynamodb_table" "main" {
  name           = "${var.project}-${var.env}-${var.service}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "service_name" 

  attribute {
    name = "service_name"
    type = "S"
  }

  tags = {
    Name = "${var.project}-${var.env}-${var.service}"
  }
}