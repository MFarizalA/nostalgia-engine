# ── OSS Bucket ───────────────────────────────────────────────────────────────
#
# Creates a private OSS bucket with:
#   - Private ACL (all access via backend-generated signed URLs only)
#   - CORS rules (allow GET/PUT from the SAS frontend origin)
#   - Lifecycle rule (auto-expire all objects after 7 days)

resource "alicloud_oss_bucket" "this" {
  bucket = var.bucket_name
  acl    = "private"

  tags = {
    Project   = "nostalgia-engine"
    ManagedBy = "opentofu"
  }
}

# ── CORS ─────────────────────────────────────────────────────────────────────
# Allows the frontend (served from SAS) to call GET on signed video URLs
# and the backend to PUT source images / generated videos.
# For production: replace allowed_origins with ["http://<sas-public-ip>"]

resource "alicloud_oss_bucket_cors" "this" {
  bucket = alicloud_oss_bucket.this.id

  rule {
    allowed_origins = var.allowed_origins
    allowed_methods = ["GET", "PUT", "HEAD"]
    allowed_headers = ["*"]
    max_age_seconds = 3600
  }
}

# ── Lifecycle — expire all objects after 7 days ───────────────────────────────

resource "alicloud_oss_bucket_lifecycle_rule" "expire_7d" {
  bucket  = alicloud_oss_bucket.this.id
  rule_id = "expire-all-objects-after-7-days"
  enabled = true
  prefix  = ""   # applies to every object in the bucket

  expiration {
    days = 7
  }
}
