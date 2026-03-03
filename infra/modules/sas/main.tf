# ── SAS instance ──────────────────────────────────────────────────────────────
#
# Provisions an Alibaba Cloud Simple Application Server (SAS / SWAS) with:
#   - Ubuntu 22.04 LTS
#   - 2 vCPU / 4 GB RAM / 40 GB SSD  (configured via var.plan_id)
#   - Cloud-init bootstrap: Docker → git clone → docker compose up
#   - 3 inbound firewall rules: SSH (22), Frontend (80), API (8000)

# ── Image lookup ─────────────────────────────────────────────────────────────
# Fetches all Ubuntu images for the region so we can auto-select Ubuntu 22.04
# if var.image_id is left empty.

data "alicloud_simple_application_server_images" "ubuntu" {
  platform = "Ubuntu"
}

locals {
  # Use var.image_id if explicitly set, otherwise pick the first Ubuntu 22.04 image
  resolved_image_id = var.image_id != "" ? var.image_id : (
    length([
      for img in data.alicloud_simple_application_server_images.ubuntu.images :
      img.id if can(regex("22.04", img.image_name))
    ]) > 0
    ? [
        for img in data.alicloud_simple_application_server_images.ubuntu.images :
        img.id if can(regex("22.04", img.image_name))
      ][0]
    : data.alicloud_simple_application_server_images.ubuntu.images[0].id
  )

  # Cloud-init rendered from template
  cloud_init = templatefile("${path.module}/cloud-init.yaml.tftpl", {
    git_repo_url          = var.git_repo_url
    dashscope_api_key     = var.dashscope_api_key
    oss_access_key_id     = var.oss_access_key_id
    oss_access_key_secret = var.oss_access_key_secret
    oss_bucket_name       = var.oss_bucket_name
    oss_endpoint          = var.oss_endpoint
  })
}

# ── Instance ──────────────────────────────────────────────────────────────────

resource "alicloud_simple_application_server_instance" "this" {
  instance_name = var.instance_name
  plan_id       = var.plan_id
  image_id      = local.resolved_image_id
  period        = var.period
  key_pair_name = var.key_pair_name != "" ? var.key_pair_name : null

  # Cloud-init — base64-encoded per the SAS API spec
  user_data = base64encode(local.cloud_init)
}

# ── Firewall rules (3×) ───────────────────────────────────────────────────────
#
# Security note (from ARCHITECTURE.md §9):
#   For production, restrict the SSH rule's source_cidr_ip to your own IP.
#   Example: source_cidr_ip = "203.0.113.42/32"

locals {
  firewall_rules = {
    ssh = {
      port        = "22"
      description = "SSH — restrict source_cidr_ip to your IP for production"
    }
    frontend = {
      port        = "80"
      description = "Frontend (Vue / nginx)"
    }
    api = {
      port        = "8000"
      description = "FastAPI backend"
    }
  }
}

resource "alicloud_simple_application_server_firewall_rule" "this" {
  for_each = local.firewall_rules

  instance_id    = alicloud_simple_application_server_instance.this.id
  rule_protocol  = "TCP"
  port           = each.value.port
  rule_direction = "in"
  description    = each.value.description
}
