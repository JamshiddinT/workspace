terraform {
  required_version = ">= 1.3.2"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.61"
    }
  }
}

provider "aws" {
  region = "us-east-1" # Use only the region, not the availability zone
}

module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  version         = "20.24.0" # Specify the module version
  cluster_name    = "my-cluster2"
  cluster_version = "1.30"
  subnet_ids      = ["subnet-0e3498f1143cda3b2", "subnet-070b06ba32474bd65"] # Corrected to subnet_ids
  vpc_id          = "vpc-0884137077183ec41"
}
