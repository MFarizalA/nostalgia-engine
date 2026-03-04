# ── Alibaba Cloud credentials ────────────────────────────────────────────────

variable "access_key" {
  description = "Alibaba Cloud access key ID. Keep out of git — use terraform.tfvars."
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Alibaba Cloud access key secret. Keep out of git — use terraform.tfvars."
  type        = string
  sensitive   = true
}

variable "region" {
  description = "Alibaba Cloud region."
  type        = string
  default     = "cn-hangzhou"
}

# ── Model Studio ─────────────────────────────────────────────────────────────

variable "dashscope_api_key" {
  description = "DashScope / Model Studio API key for Qwen + Wan."
  type        = string
  sensitive   = true
}

# ── OSS ──────────────────────────────────────────────────────────────────────

variable "oss_bucket_name" {
  description = <<-EOT
    OSS bucket name for generated videos and source images.
    Must be globally unique. Recommended: nostalgia-engine-outputs-<yourname>.
  EOT
  type        = string
}

# ── SAS ──────────────────────────────────────────────────────────────────────

variable "sas_instance_name" {
  description = "Display name for the SAS instance."
  type        = string
  default     = "doge-nostalgia-engine"
}

variable "sas_plan_id" {
  description = <<-EOT
    SAS instance plan ID (2 vCPU / 4 GB RAM / 40 GB SSD).
    Find available plans:
      tofu console → data.alicloud_simple_application_server_server_plans.all.plans
    or via Alibaba Cloud console → Simple Application Server → Plans.
    Example (cn-hangzhou): swas.s2.medium.1
  EOT
  type        = string
}

variable "sas_image_id" {
  description = <<-EOT
    SAS OS image ID for Ubuntu 22.04 LTS.
    Leave empty to auto-select the first Ubuntu 22.04 image for your region.
    Find available images:
      tofu console → data.alicloud_simple_application_server_images.ubuntu.images
  EOT
  type    = string
  default = ""
}

variable "sas_period" {
  description = "Billing period in months (1, 3, 6, 12, 24, 36)."
  type        = number
  default     = 1

  validation {
    condition     = contains([1, 3, 6, 12, 24, 36], var.sas_period)
    error_message = "sas_period must be one of: 1, 3, 6, 12, 24, 36."
  }
}

variable "key_pair_name" {
  description = <<-EOT
    Name of an existing SAS key pair for SSH access.
    Create one in the Alibaba Cloud console → Simple Application Server → Key Pairs.
  EOT
  type    = string
  default = ""
}

# ── App ───────────────────────────────────────────────────────────────────────

variable "git_repo_url" {
  description = "Git repository URL cloned on the SAS instance during cloud-init bootstrap."
  type        = string
  default     = "https://github.com/your-org/nostalgia-engine.git"
}

variable "ssh_private_key_path" {
  description = "Local path to the .pem key file for SSH bootstrap (e.g. ~/doge-nostalgia-engine-key.pem)."
  type        = string
}
