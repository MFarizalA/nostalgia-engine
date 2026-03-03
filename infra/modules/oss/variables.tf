variable "bucket_name" {
  description = "OSS bucket name. Must be globally unique."
  type        = string
}

variable "allowed_origins" {
  description = <<-EOT
    List of allowed CORS origins.
    Default is ["*"] for hackathon convenience.
    For production: set to ["http://<sas-public-ip>"] after first apply.
  EOT
  type    = list(string)
  default = ["*"]
}
