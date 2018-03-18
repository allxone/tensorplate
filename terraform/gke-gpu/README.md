# Cluster provisioning

## Prerequisites
- terraform 0.11.4
- gcloud
- kubectl

'''
# Create cluster (initial state: 1 alwayson + 0 preemptible nodes)
terraform init -upgrade
terraform apply

# Download kubectl context () 
gcloud container clusters get-credentials gke-gpu --zone us-central1-a --project datalab-192808
kubectl create -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/k8s-1.9/nvidia-driver-installer/cos/daemonset-preloaded.yaml

# Overcame current terraform limitation: https://github.com/terraform-providers/terraform-provider-kubernetes/issues/149
kubectl delete pod model
kubectl create -f model.yaml
'''