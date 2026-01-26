terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.0.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = "EUROPE"
  access_token = "fake-emulator-token"
  storage_custom_endpoint = "http://localhost:4443/storage/v1/"
}

resource "google_storage_bucket" "demo-bucket" {
  name          = "${var.project}-terra-bucket"
  location      = "EUROPE"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}
