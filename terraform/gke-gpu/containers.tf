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
      port        = "${var.mqtt_port}"
      target_port = "${var.mqtt_port}"
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_pod" "model" {
  metadata {
    name = "model"

    labels {
      App = "model"
    }
  }

  spec {
    node_selector {
      "cloud.google.com/gke-nodepool"    = "preemptible"
      "cloud.google.com/gke-accelerator" = "nvidia-tesla-k80"
    }

    container {
      image             = "allxone/tensorplate:model-tfserving-broken"
      name              = "model"
      image_pull_policy = "Always"

      port {
        container_port = "${var.scoring_port}"
      }

      # Unsupported:
      #  https://github.com/terraform-providers/terraform-provider-kubernetes/issues/149
      # Untaint workaround:
      #  kubectl taint nodes gke-gke-gpu-pool-preemptible-76752dd8-fqbn nvidia.com/gpu:NoSchedule-
      # Manual edit workaround:
      #  manually modify pod yaml from gke web console to add the extended resource request
      # Always run:
      #  kubectl create -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/k8s-1.9/nvidia-driver-installer/cos/daemonset-preloaded.yaml
      # resources {
      #   requests {
      #     "nvidia/gpu" = "1"
      #   }
      # }
    }
  }
}

resource "kubernetes_service" "model" {
  metadata {
    name = "model"
  }

  spec {
    selector {
      App = "${kubernetes_pod.model.metadata.0.labels.App}"
    }

    port {
      port        = "${var.scoring_port}"
      target_port = "${var.scoring_port}"
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_pod" "mqtt-tfserving" {
  metadata {
    name = "mqtt-tfserving"

    labels {
      App = "mqtt-tfserving"
    }
  }

  spec {
    container {
      image             = "allxone/tensorplate:mqtt-tfserving"
      name              = "mqtt-tfserving"
      image_pull_policy = "Always"

      env {
        name  = "SCORING_ADDRESS"
        value = "${kubernetes_service.model.load_balancer_ingress.0.ip}:${var.scoring_port}"
      }

      env {
        name  = "MQTT_SERVER"
        value = "${kubernetes_service.mosquitto.load_balancer_ingress.0.ip}"
      }

      env {
        name  = "MQTT_SERVER_PORT"
        value = "${var.mqtt_port}"
      }

      env {
        name  = "TFS_TIMEOUT"
        value = "${var.tfs_timeout}"
      }

      env {
        name  = "TFS_THRESHOLD"
        value = "${var.tfs_threshold}"
      }
    }
  }
}

output "lb_ip" {
  value = "${kubernetes_service.mosquitto.load_balancer_ingress.0.ip}"
}

output "scoring_address" {
  value = "${kubernetes_service.model.load_balancer_ingress.0.ip}:${var.scoring_port}"
}
