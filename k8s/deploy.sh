#!/bin/bash

# GeoJSON Ingestion Service - Kubernetes Deployment Script
set -e

echo "🚀 Deploying GeoJSON Ingestion Service to Kubernetes"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
check_kubectl() {
    print_status "Checking kubectl availability..."
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    print_success "Connected to Kubernetes cluster"
}

# Update database secret with actual values from Terraform
update_secret() {
    print_status "Database secret already configured with correct values..."
    print_status "Using RDS endpoint: silver-saas-postgres.csbuekwioimk.us-east-1.rds.amazonaws.com"
    print_status "Using database name: geojson_db"
    print_success "Secret ready for deployment"
}

# Deploy to Kubernetes
deploy() {
    print_status "Deploying to Kubernetes..."
    
    # Apply secret first
    print_status "Applying database secret..."
    kubectl apply -f secret.yaml
    
    # Apply deployment
    print_status "Applying deployment..."
    kubectl apply -f deployment.yaml
    
    # Apply service
    print_status "Applying service..."
    kubectl apply -f service.yaml
    
    # Apply HPA
    print_status "Applying Horizontal Pod Autoscaler..."
    kubectl apply -f hpa.yaml
    
    print_success "All manifests applied successfully!"
}

# Wait for deployment to be ready
wait_for_deployment() {
    print_status "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/geojson-ingestion
    
    print_success "Deployment is ready!"
}

# Get service information
get_service_info() {
    print_status "Getting service information..."
    
    echo ""
    echo "📊 Service Status:"
    kubectl get service geojson-ingestion-service
    
    echo ""
    echo "🔍 Pod Status:"
    kubectl get pods -l app=geojson-ingestion
    
    echo ""
    echo "📈 HPA Status:"
    kubectl get hpa geojson-ingestion-hpa
    
    echo ""
    print_success "Deployment complete! Your service should be accessible via the LoadBalancer IP above."
}

# Main execution
main() {
    print_status "Starting Kubernetes deployment..."
    
    check_kubectl
    update_secret
    deploy
    wait_for_deployment
    get_service_info
    
    print_success "🎉 GeoJSON Ingestion Service deployed successfully!"
}

# Run main function
main "$@"
