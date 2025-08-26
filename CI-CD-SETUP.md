# 🚀 CI/CD Pipeline Setup Guide

## 📋 Prerequisites

✅ **Already Complete:**
- FastAPI app with Dockerfile
- Kubernetes manifests (deployment, service, HPA, secret)
- EKS cluster running
- ECR repository created
- App successfully deployed manually

## 🔑 Required GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AWS_ACCESS_KEY_ID` | `AKIA...` | Your AWS IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | `...` | Your AWS IAM user secret key |
| `AWS_REGION` | `us-east-1` | AWS region where EKS/ECR are located |
| `ECR_REGISTRY` | `826331272066.dkr.ecr.us-east-1.amazonaws.com` | Your ECR registry URL |
| `ECR_REPOSITORY` | `silver-saas-geojson-ingestion` | Your ECR repository name |

## 🛠️ IAM User Permissions

Your IAM user needs these policies:
- `AmazonEKSClusterPolicy`
- `AmazonEKSWorkerNodePolicy` 
- `AmazonEC2ContainerRegistryFullAccess`

## 📁 Repository Structure

```
applications/geojson-ingestion/
├── .github/
│   └── workflows/
│       └── deploy.yml          ← CI/CD pipeline
├── app/
│   └── main.py
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   └── secret.yaml
├── Dockerfile
└── requirements.txt
```

## 🚀 How to Test

1. **Make a small change** to your code (e.g., add a comment in `main.py`)

2. **Commit and push:**
   ```bash
   git add .
   git commit -m "test: CI/CD pipeline"
   git push origin main
   ```

3. **Watch the magic:**
   - Go to GitHub → **Actions** tab
   - See your workflow running automatically
   - Watch it build, push to ECR, and deploy to EKS

## 🔍 What Happens on Each Push

1. **Code checkout** from GitHub
2. **Docker build** of your app
3. **Push to ECR** with latest tag
4. **Deploy to EKS** using kubectl
5. **Health check** and status report

## 🎯 Benefits

- **Zero-downtime deployments**
- **Automatic rollbacks** on failure
- **Consistent deployments** every time
- **No more manual kubectl commands**
- **Production-ready CI/CD pipeline**

## 🚨 Troubleshooting

**Common Issues:**
- **IAM permissions**: Ensure your IAM user has all required policies
- **ECR authentication**: Check ECR_REGISTRY and ECR_REPOSITORY secrets
- **EKS access**: Verify CLUSTER_NAME matches your actual cluster

**Debug Commands:**
```bash
# Check EKS cluster name
aws eks list-clusters --region us-east-1

# Check ECR repositories
aws ecr describe-repositories --region us-east-1

# Verify kubectl access
kubectl get nodes
```

## 🎉 You're Ready!

Once you add the GitHub secrets, every push to `main` will automatically:
1. Build your Docker image
2. Push to ECR
3. Deploy to EKS
4. Update your production service

**No more manual deployments!** 🚀
