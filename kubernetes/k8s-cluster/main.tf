provider "aws" {
  region = "us-west-2"
}

module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "my-cluster"
  cluster_version = "1.26"
  subnets         = ["subnet-12345", "subnet-67890"]
  vpc_id          = "vpc-12345"
}
