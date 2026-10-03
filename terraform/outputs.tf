output "postgres_url" {
  description = "Postgres connection URL for the sandbox RDS instance (psycopg driver)"
  value = format(
    "postgresql+psycopg://%s:%s@%s:%s/%s",
    urlencode(var.db_username),
    urlencode(var.db_password),
    aws_db_instance.sandbox_postgres.address,
    aws_db_instance.sandbox_postgres.port,
    urlencode(var.db_name),
  )
  sensitive = true
}

output "postgres_endpoint" {
  description = "Hostname:port for the sandbox Postgres RDS instance"
  value       = aws_db_instance.sandbox_postgres.endpoint
}

output "app_instance_id" {
  description = "EC2 instance ID for SSM Session Manager"
  value       = aws_instance.app_instance.id
}

output "instance_role_arn" {
  description = "IAM role ARN attached to the app instance for SSM"
  value       = aws_iam_role.instance_role.arn
}

