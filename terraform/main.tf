terraform {
  backend "s3" {
    bucket  = "s3-terraform-state.stedel.it"
    key     = "converge/hackathon.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

// Configure the Google Cloud provider
provider "google" {
  credentials = "${file("security/gcp-datalab.json")}"
  project     = "datalab-192808"
  region      = "us-central1"
}

resource "google_container_cluster" "primary" {
  name               = "converge-hackaton"
  zone               = "us-central1-a"
  initial_node_count = 1

  additional_zones = [
    "us-central1-b",
    "us-central1-c",
  ]

  master_auth {
    username = "hackathon"
    password = "convergehackathon.org"
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

provider "kubernetes" {
  host     = "https://${google_container_cluster.primary.endpoint}"
  username = "${google_container_cluster.primary.master_auth.0.username}"
  password = "${google_container_cluster.primary.master_auth.0.password}"

  client_certificate     = "${base64decode(google_container_cluster.primary.master_auth.0.client_certificate)}"
  client_key             = "${base64decode(google_container_cluster.primary.master_auth.0.client_key)}"
  cluster_ca_certificate = "${base64decode(google_container_cluster.primary.master_auth.0.cluster_ca_certificate)}"
}

resource "kubernetes_pod" "nginx" {
  metadata {
    name = "nginx-example"
    labels {
      App = "nginx"
    }
  }

  spec {
    container {
      image = "nginx:1.7.8"
      name  = "example"

      port {
        container_port = 80
      }
    }
  }
}

resource "kubernetes_service" "nginx" {
  metadata {
    name = "nginx-example"
  }
  spec {
    selector {
      App = "${kubernetes_pod.nginx.metadata.0.labels.App}"
    }
    port {
      port = 80
      target_port = 80
    }

    type = "LoadBalancer"
  }
}

output "lb_ip" {
  value = "${kubernetes_service.nginx.load_balancer_ingress.0.ip}"
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