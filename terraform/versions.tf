terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws    = ">= 5.60.0"
    random = ">= 3.5.0"
  }

  backend "remote" {}
}