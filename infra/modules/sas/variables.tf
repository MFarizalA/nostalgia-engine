variable "instance_name" {
  description = "Display name for the SAS instance."
  type        = string
  default     = "doge-nostalgia-engine"
}

variable "plan_id" {
  description = "SAS instance plan ID (e.g. swas.s.c2m2s40b1.linux)."
  type        = string
}

variable "image_id" {
  description = "SAS image ID. Leave empty to auto-select Ubuntu 22.04."
  type        = string
  default     = ""
}

variable "period" {
  description = "Billing period in months."
  type        = number
  default     = 1
}
