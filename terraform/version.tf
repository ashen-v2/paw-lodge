terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>6.60.0"
    }
  }
  required_version = ">= 1.5.0"

  cloud {
    organization = "my-learning231"

    workspaces {
      name = "paw-lodge"
    }
  }

}