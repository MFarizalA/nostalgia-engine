terraform {
  required_version = ">= 1.6"

  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.220"
    }
  }

  # ── Remote state (uncomment for team use) ───────────────────────────────
  # backend "oss" {
  #   bucket = "your-tofu-state-bucket"
  #   prefix = "nostalgia-engine/tfstate"
  #   region = "cn-hangzhou"
  # }
}

provider "alicloud" {
  access_key = var.access_key
  secret_key = var.secret_key
  region     = var.region
}

# ── OSS bucket (provisioned first — SAS cloud-init needs the bucket name) ──

module "oss" {
  source = "./modules/oss"

  providers = { alicloud = alicloud }

  bucket_name     = var.oss_bucket_name
  allowed_origins = ["*"] 
}

# ── Simple Application Server ────────────────────────────────────────────────

module "sas" {
  source = "./modules/sas"

  providers  = { alicloud = alicloud }
  depends_on = [module.oss]

  instance_name = var.sas_instance_name
  plan_id       = var.sas_plan_id
  image_id      = var.sas_image_id
  period        = var.sas_period
}
