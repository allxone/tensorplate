// Configure the Google Cloud provider
provider "google" {
  credentials = "${file("security/gcp-datalab.json")}"
  project     = "datalab-192808"
  region      = "us-central1"
}

resource "google_container_cluster" "primary" {
  name               = "converge-hackaton"
  zone               = "us-central1-a"
  initial_node_count = "${var.initial_node_count}"

  additional_zones = [
    "us-central1-c",
    "us-central1-f",
  ]

  master_auth {
    username = "hackathon"
    password = "${var.kubernetes_password}"
  }

  node_config {
    oauth_scopes = [
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    labels {
      role = "kubernetes"
    }

    tags = ["role", "kubernetes"]
  }
}

# The following outputs allow authentication and connectivity to the GKE Cluster.
# output "client_certificate" {
#   value = "${google_container_cluster.primary.master_auth.0.client_certificate}"
# }

# output "client_key" {
#   value = "${google_container_cluster.primary.master_auth.0.client_key}"
# }

# output "cluster_ca_certificate" {
#   value = "${google_container_cluster.primary.master_auth.0.cluster_ca_certificate}"
# }