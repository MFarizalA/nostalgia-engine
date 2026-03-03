variable "instance_name" {
  description = "Display name for the SAS instance."
  type        = string
  default     = "doge-nostalgia-engine"
}

variable "plan_id" {
  description = <<-EOT
    SAS plan ID specifying vCPU / RAM / SSD.
    Target: 2 vCPU / 4 GB RAM / 40 GB SSD.
    Find available plans for your region:
      tofu console → data.alicloud_simple_application_server_server_plans.all.plans
    Example (cn-hangzhou): swas.s2.medium.1
  EOT
  type = string
}

variable "image_id" {
  description = <<-EOT
    SAS image ID for Ubuntu 22.04 LTS.
    Leave empty ("") to auto-select the first Ubuntu 22.04 image for the region.
  EOT
  type    = string
  default = ""
}

variable "period" {
  description = "Billing period in months."
  type        = number
  default     = 1
}

variable "key_pair_name" {
  description = "Name of an existing SAS key pair for SSH access. Leave empty to skip."
  type        = string
  default     = ""
}

# ── Secrets passed into cloud-init ───────────────────────────────────────────

variable "dashscope_api_key" {
  description = "DashScope / Model Studio API key written into the server .env."
  type        = string
  sensitive   = true
}

variable "oss_access_key_id" {
  description = "Alibaba Cloud access key ID written into the server .env."
  type        = string
  sensitive   = true
}

variable "oss_access_key_secret" {
  description = "Alibaba Cloud access key secret written into the server .env."
  type        = string
  sensitive   = true
}

variable "oss_bucket_name" {
  description = "OSS bucket name written into the server .env."
  type        = string
}

variable "oss_endpoint" {
  description = "OSS endpoint written into the server .env."
  type        = string
}

variable "git_repo_url" {
  description = "Git repository URL cloned during cloud-init bootstrap."
  type        = string
  default     = "https://github.com/your-org/nostalgia-engine.git"
}
