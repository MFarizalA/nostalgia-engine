output "app_url" {
  description = "Frontend URL (port 80)."
  value       = "http://${module.sas.public_ip}"
}

output "api_url" {
  description = "FastAPI backend URL (port 8000). Swagger UI at /docs."
  value       = "http://${module.sas.public_ip}:8000"
}

output "api_docs_url" {
  description = "FastAPI Swagger UI."
  value       = "http://${module.sas.public_ip}:8000/docs"
}

output "ssh_command" {
  description = "SSH command to connect to the SAS instance."
  value       = "ssh root@${module.sas.public_ip}"
}

output "sas_instance_id" {
  description = "SAS instance ID."
  value       = module.sas.instance_id
}

output "oss_bucket" {
  description = "OSS bucket name for generated video outputs."
  value       = module.oss.bucket_name
}

output "oss_endpoint" {
  description = "OSS endpoint used by the backend."
  value       = module.oss.endpoint
}
