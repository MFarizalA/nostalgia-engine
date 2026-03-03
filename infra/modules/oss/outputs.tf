output "bucket_name" {
  description = "The OSS bucket name."
  value       = alicloud_oss_bucket.this.id
}

output "bucket_domain" {
  description = "Internal OSS bucket domain (used by backend within the same region)."
  value       = alicloud_oss_bucket.this.intranet_endpoint
}

output "endpoint" {
  description = "OSS regional endpoint passed to the backend as OSS_ENDPOINT."
  value       = alicloud_oss_bucket.this.extranet_endpoint
}
