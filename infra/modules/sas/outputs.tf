output "instance_id" {
  description = "SAS instance ID."
  value       = alicloud_simple_application_server_instance.this.id
}

output "public_ip" {
  description = "Public IP of the SAS instance."
  value       = try(data.alicloud_simple_application_server_instances.this.instances[0].public_ip_address, "Check Alibaba Cloud console for public IP")
}
