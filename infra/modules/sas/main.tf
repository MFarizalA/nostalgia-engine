terraform {
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.220"
    }
  }
}

# ── Image lookup ─────────────────────────────────────────────────────────────

data "alicloud_simple_application_server_images" "ubuntu" {
  platform = "Linux"
}

locals {
  # Auto-select Ubuntu 22.04 image; override via var.image_id
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
}

# ── Instance ──────────────────────────────────────────────────────────────────

resource "alicloud_simple_application_server_instance" "this" {
  instance_name = var.instance_name
  plan_id       = var.plan_id
  image_id      = local.resolved_image_id
  period        = var.period
}

# ── Firewall rules (3×) ───────────────────────────────────────────────────────
# Note: rule_protocol must be "Tcp", "Udp", or "TcpAndUdp" (title-case)

resource "alicloud_simple_application_server_firewall_rule" "this" {
  for_each = {
    ssh      = "22"
    frontend = "80"
    api      = "8000"
  }

  instance_id   = alicloud_simple_application_server_instance.this.id
  rule_protocol = "Tcp"
  port          = each.value
}

# ── Fetch instance details (public IP) ───────────────────────────────────────

data "alicloud_simple_application_server_instances" "this" {
  ids        = [alicloud_simple_application_server_instance.this.id]
  depends_on = [alicloud_simple_application_server_instance.this]
}
