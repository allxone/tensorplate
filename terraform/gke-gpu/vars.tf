variable "kubernetes_version" {
  default = "1.9.2"
}

variable "cloud_zone" {
  default = "us-central1-a"
}

variable "initial_node_count" {
    description = "Minions"
    default = "1"
}

variable "kubernetes_password" {
    description = "Kubernetes password"
}

variable "scoring_port" {
  description = "Scoring port"
  default = "80"
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