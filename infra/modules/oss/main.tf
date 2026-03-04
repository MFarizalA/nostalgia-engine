terraform {
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.220"
    }
  }
}

# ── OSS Bucket ───────────────────────────────────────────────────────────────
#
# Creates a private OSS bucket with:
#   - Private ACL (all access via backend-generated signed URLs only)
#   - CORS rules (allow GET/PUT from the SAS frontend origin)
#   - Lifecycle rule (auto-expire all objects after 7 days)

resource "alicloud_oss_bucket" "this" {
  bucket = var.bucket_name

  # ── CORS ───────────────────────────────────────────────────────────────────
  # For production: replace allowed_origins with ["http://<sas-public-ip>"]
  cors_rule {
    allowed_origins = var.allowed_origins
    allowed_methods = ["GET", "PUT", "HEAD"]
    allowed_headers = ["*"]
    max_age_seconds = 3600
  }

  # ── Lifecycle — auto-delete all objects after 7 days ──────────────────────
  lifecycle_rule {
    id      = "expire-7d"
    enabled = true
    prefix  = ""

    expiration {
      days = 7
    }
  }

  tags = {
    Project   = "nostalgia-engine"
    ManagedBy = "opentofu"
  }
}

resource "alicloud_oss_bucket_acl" "this" {
  bucket = alicloud_oss_bucket.this.id
  acl    = "private"
}
