output "instance_id" {
  description = "SAS instance ID."
  value       = alicloud_simple_application_server_instance.this.id
}

output "public_ip" {
  description = "Public IPv4 address of the SAS instance."
  value       = alicloud_simple_application_server_instance.this.public_ip_address
}
