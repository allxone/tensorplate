// Configure the Google Cloud provider
provider "google" {
  credentials = "${file("security/gcp-datalab.json")}"
  project     = "datalab-192808"
  region      = "us-central1"
}

// Cluster features:
// - single zone cluster (no HA required)
// - default pool with a single low-profile VM (non prehentible)
// - GPU pool with preventible VMs (last 24h max)
// - gke alpha options

// GET CREDENTIALS X kubectl: gcloud container clusters get-credentials gke-gpu-pool --zone us-central1-a --project datalab-192808

resource "google_container_cluster" "primary" {
  name                    = "gke-gpu"
  zone                    = "${var.cloud_zone}"
  enable_kubernetes_alpha = true
  node_version            = "${var.kubernetes_version}"
  min_master_version      = "${var.min_master_version}"

  master_auth {
    username = "gke-gpu"
    password = "${var.kubernetes_password}"
  }

  // https://github.com/terraform-providers/terraform-provider-google/pull/299
  node_pool {
    name       = "alwayson"
    node_count = "${var.alwayson_node_count}"

    node_config {
      machine_type = "n1-standard-1"
      disk_size_gb = 10
      preemptible  = false

      oauth_scopes = [
        "https://www.googleapis.com/auth/compute",
        "https://www.googleapis.com/auth/devstorage.read_only",
        "https://www.googleapis.com/auth/logging.write",
        "https://www.googleapis.com/auth/monitoring",
      ]

      labels {
        role = "kubernetes"
        pool = "alwayson"
      }

      tags = ["role", "kubernetes"]
    }
  }

  node_pool {
    name       = "preemptible"
    node_count = "${var.preemptible_node_count}"

    # GPU pool starts with zero nodes and autoscale if required (tested) 
    autoscaling {
      min_node_count = 0
      max_node_count = 1
    }

    node_config {
      machine_type = "n1-standard-1"
      disk_size_gb = 30
      preemptible  = true

      // Thanks to https://github.com/terraform-providers/terraform-provider-google/issues/1067
      guest_accelerator {
        type  = "nvidia-tesla-k80"
        count = 1
      }

      labels {
        role = "kubernetes"
        pool = "preemptible"
      }

      tags = ["role", "kubernetes"]
    }
  }
}

output "cluster_name" {
  value = "${google_container_cluster.primary.name}"
}

output "primary_zone" {
  value = "${google_container_cluster.primary.zone}"
}

output "endpoint" {
  value = "${google_container_cluster.primary.endpoint}"
}

output "node_version" {
  value = "${google_container_cluster.primary.node_version}"
}

# The following outputs allow authentication and connectivity to the GKE Cluster.
output "client_certificate" {
  value = "${google_container_cluster.primary.master_auth.0.client_certificate}"
}

output "client_key" {
  value = "${google_container_cluster.primary.master_auth.0.client_key}"
}

output "cluster_ca_certificate" {
  value = "${google_container_cluster.primary.master_auth.0.cluster_ca_certificate}"
}
