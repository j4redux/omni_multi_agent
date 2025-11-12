output "cluster_id" {
  description = "ECS Cluster ID"
  value       = aws_ecs_cluster.main.id
}

output "cluster_name" {
  description = "ECS Cluster name"
  value       = aws_ecs_cluster.main.name
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "efs_id" {
  description = "EFS File System ID"
  value       = aws_efs_file_system.letta_data.id
}

output "log_group_name" {
  description = "CloudWatch Log Group name"
  value       = aws_cloudwatch_log_group.ecs.name
}

output "anthropic_secret_arn" {
  description = "Anthropic API key secret ARN"
  value       = aws_secretsmanager_secret.anthropic_key.arn
  sensitive   = true
}

output "openai_secret_arn" {
  description = "OpenAI API key secret ARN"
  value       = aws_secretsmanager_secret.openai_key.arn
  sensitive   = true
}
