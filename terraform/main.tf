variable "initial_node_count" {
    description = "Minions"
    default = "1"
}

variable "kubernetes_password" {
    description = "Kubernetes password"
}

variable "flask_port" {
    description = "Flask port"
    default = "8888"
}

variable "mqtt_port" {
    description = "MQTT port"
    default = "1883"
}

terraform {
  backend "s3" {
    bucket  = "s3-terraform-state.stedel.it"
    key     = "converge/hackathon3.tfstate"
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

provider "kubernetes" {
  host     = "https://${google_container_cluster.primary.endpoint}"
  username = "${google_container_cluster.primary.master_auth.0.username}"
  password = "${google_container_cluster.primary.master_auth.0.password}"

  client_certificate     = "${base64decode(google_container_cluster.primary.master_auth.0.client_certificate)}"
  client_key             = "${base64decode(google_container_cluster.primary.master_auth.0.client_key)}"
  cluster_ca_certificate = "${base64decode(google_container_cluster.primary.master_auth.0.cluster_ca_certificate)}"
}

resource "kubernetes_pod" "mosquitto" {
  metadata {
    name = "mosquitto"
    labels {
      App = "mosquitto"
    }
  }

  spec {
    container {
      image = "toke/mosquitto"
      name  = "mosquitto"
      port {
        container_port = "${var.mqtt_port}"
      }
      # port {
      #   container_port = 9001
      # }
    }
  }
}

resource "kubernetes_service" "mosquitto" {
  metadata {
    name = "mosquitto-service"
  }
  spec {
    selector {
      App = "${kubernetes_pod.mosquitto.metadata.0.labels.App}"
    }
    port {
      port = "${var.mqtt_port}"
      target_port = "${var.mqtt_port}"
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_pod" "scoring" {
  metadata {
    name = "scoring"
    labels {
      App = "scoring"
    }
  }

  spec {
    container {
      image = "allxone/tensorplate:Cleanup"
      name  = "scoring"

      env {
        name = "FLASK_PORT"
        value = "${var.flask_port}"
      }
      env {
        name = "MQTT_SERVER"
        value = "${kubernetes_service.mosquitto.load_balancer_ingress.0.ip}"
      }
      env {
        name = "MQTT_SERVER_PORT"
        value = "${var.mqtt_port}"
      }
      port {
        container_port = "${var.flask_port}"
      }
    }
  }
}

resource "kubernetes_service" "scoring" {
  metadata {
    name = "scoring-service"
  }
  spec {
    selector {
      App = "${kubernetes_pod.scoring.metadata.0.labels.App}"
    }
    port {
      port = "${var.flask_port}"
      target_port = "${var.flask_port}"
    }

    type = "LoadBalancer"
  }
}

output "lb_ip" {
  value = "${kubernetes_service.mosquitto.load_balancer_ingress.0.ip}"
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