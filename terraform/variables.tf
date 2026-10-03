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

variable "app_instance_type" {
  description = "Instance type for the application instance"
  type        = string
  default     = "t3.micro"
}

variable "db_name" {
  description = "Initial database name for the sandbox Postgres RDS instance"
  type        = string
  default     = "pawlodge"
}

variable "db_username" {
  description = "Master username for the sandbox Postgres RDS instance"
  type        = string
  default     = "pawlodge"
}

variable "db_password" {
  description = "Master password for the sandbox Postgres RDS instance"
  type        = string
  sensitive   = true
  default     = "pawlodge"
}

variable "db_instance_class" {
  description = "Instance class for the sandbox Postgres RDS instance"
  type        = string
  default     = "db.t4g.micro"
}