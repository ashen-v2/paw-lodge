variable "global_tag" {
  description = "Global tag for all resources"
  type        = map(string)
  default = {
    "Project" = "ZeroToShip"
  }
}

variable "availability_zones" {
  description = "List of availability zones to use for the VPC"
  type        = list(string)
  default     = ["ap-southeast-1a", "ap-southeast-1b"]
}

variable "app_ami" {
  description = "AMI ID for the application instance"
  type        = string
  default     = "ami-0c55b159cbfafe1f0" # Replace with your desired AMI ID
}

variable "app_instance_type" {
  description = "Instance type for the application instance"
  type        = string
  default     = "t3.micro"
}