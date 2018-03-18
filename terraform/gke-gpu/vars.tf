variable "kubernetes_version" {
  default = "1.9.4-gke.1"
}

variable "min_master_version" {
  default = "1.9.4"
}

variable "cloud_zone" {
  default = "us-central1-a"
}

variable "alwayson_node_count" {
  description = "Alwayson pool Node count "
  default     = "1"
}

variable "preemptible_node_count" {
  description = "Preemptible pool Node count "
  default     = "1"
}

variable "kubernetes_password" {
  description = "Kubernetes password"
}

variable "scoring_port" {
  description = "Scoring port"
  default     = "9000"
}

variable "mqtt_port" {
  description = "MQTT port"
  default     = "1883"
}

terraform {
  backend "s3" {
    bucket  = "s3-terraform-state.stedel.it"
    key     = "converge/hackathon3.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}
