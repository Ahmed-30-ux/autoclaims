#!/bin/bash
# ==============================================================
# AutoClaims - Alibaba Cloud Deployment Script
# Track 4: Autopilot Agent — Qwen Cloud Global AI Hackathon
# ==============================================================
# Prerequisites:
#   1. Alibaba Cloud ECS instance (Ubuntu 22.04+ recommended)
#   2. Docker and docker-compose installed on the instance
#   3. Qwen API key (set as env var or in backend/.env)
#   4. Security group rules: ports 80, 443, 8000, 3010 open
#
# Quick start:
#   chmod +x alibaba-deploy.sh
#   export QWEN_API_KEY="sk-ws-..."
#   ./alibaba-deploy.sh
# ==============================================================

set -euo pipefail

# ======================= CONFIGURATION =======================
# Edit these before running
ECS_PUBLIC_IP="${ECS_PUBLIC_IP:-}"          # Your ECS instance public IP
ECS_USER="${ECS_USER:-root}"                # SSH user
REMOTE_DIR="${REMOTE_DIR:-/root/autoclaims}"  # Remote install dir
QWEN_API_KEY="${QWEN_API_KEY:-}"             # Qwen Cloud API key
DOMAIN="${DOMAIN:-}"                          # Optional: custom domain

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  AutoClaims — Alibaba Cloud Deployment${NC}"
echo -e "${BLUE}================================================${NC}"

# ======================= CHECKS =======================
if [ -z "$ECS_PUBLIC_IP" ]; then
    echo -e "${YELLOW}ECS_PUBLIC_IP not set. Using local docker-compose only.${NC}"
    echo -e "${YELLOW}Set ECS_PUBLIC_IP to deploy to a remote ECS instance.${NC}"
    LOCAL_ONLY=true
else
    LOCAL_ONLY=false
fi

if [ -z "$QWEN_API_KEY" ]; then
    if [ -f "../backend/.env" ]; then
        echo -e "${GREEN}Using QWEN_API_KEY from backend/.env${NC}"
        export QWEN_API_KEY=$(grep QWEN_API_KEY ../backend/.env | cut -d '=' -f2)
    else
        echo -e "${RED}ERROR: QWEN_API_KEY not set and not found in backend/.env${NC}"
        echo -e "${YELLOW}Set it with: export QWEN_API_KEY='sk-ws-...'${NC}"
        exit 1
    fi
fi

# ======================= BUILD =======================
echo -e "\n${BLUE}[1/5] Building Docker images...${NC}"

cd "$(dirname "$0")/.."

# Build backend image
docker build -t autoclaims-backend:latest -f Dockerfile.backend .

# Build frontend image
docker build -t autoclaims-frontend:latest -f Dockerfile.frontend .

echo -e "${GREEN}✓ Images built successfully${NC}"

# ======================= LOCAL TEST =======================
if [ "$LOCAL_ONLY" = true ]; then
    echo -e "\n${BLUE}[2/5] Local deployment with docker-compose...${NC}"
    export QWEN_API_KEY="$QWEN_API_KEY"
    docker compose down 2>/dev/null || true
    docker compose up -d
    echo -e "${GREEN}✓ Local deployment complete${NC}"
    echo -e "  Frontend: http://localhost:3010"
    echo -e "  Backend:  http://localhost:8000/api/health"
    echo -e "  Claim it's working: curl http://localhost:8000/api/claims"
    exit 0
fi

# ======================= REMOTE DEPLOY =======================
echo -e "\n${BLUE}[2/5] Saving Docker images...${NC}"
docker save autoclaims-backend:latest | gzip > backend.tar.gz
docker save autoclaims-frontend:latest | gzip > frontend.tar.gz
echo -e "${GREEN}✓ Images saved${NC}"

echo -e "\n${BLUE}[3/5] Preparing remote instance...${NC}"
ssh "${ECS_USER}@${ECS_PUBLIC_IP}" "mkdir -p ${REMOTE_DIR}" || {
    echo -e "${RED}Failed to connect to ECS instance. Check ECS_PUBLIC_IP and SSH access.${NC}"
    exit 1
}

# Copy files
echo -e "\n${BLUE}[4/5] Copying files to ECS...${NC}"
scp backend.tar.gz frontend.tar.gz docker-compose.yml "${ECS_USER}@${ECS_PUBLIC_IP}:${REMOTE_DIR}/"

# Deploy on remote
echo -e "\n${BLUE}[5/5] Deploying on ECS...${NC}"
ssh "${ECS_USER}@${ECS_PUBLIC_IP}" << EOF
    cd ${REMOTE_DIR}
    
    # Load images
    gunzip -c backend.tar.gz | docker load
    gunzip -c frontend.tar.gz | docker load
    
    # Clean up tar files
    rm -f backend.tar.gz frontend.tar.gz
    
    # Set environment
    export QWEN_API_KEY="${QWEN_API_KEY}"
    
    # Stop existing containers
    docker compose down 2>/dev/null || true
    
    # Start services
    docker compose up -d
    
    # Verify
    echo ""
    echo "Checking services..."
    sleep 3
    curl -s http://localhost:8000/api/health | head -c 200
    echo ""
EOF

# ======================= VERIFICATION =======================
echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
echo -e "  Frontend: ${GREEN}http://${ECS_PUBLIC_IP}:3010${NC}"
echo -e "  Backend:  ${GREEN}http://${ECS_PUBLIC_IP}:8000/api/health${NC}"
echo -e ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Wait 30s for containers to start fully"
echo -e "  2. Check: curl http://${ECS_PUBLIC_IP}:8000/api/health"
echo -e "  3. Open http://${ECS_PUBLIC_IP}:3010 in browser"
echo -e "  4. For production, configure Nginx reverse proxy + SSL"
echo -e ""
echo -e "${BLUE}Proof of deployment (capture as screenshot):${NC}"
echo -e "  curl http://${ECS_PUBLIC_IP}:8000/api/health"
echo -e "  curl http://${ECS_PUBLIC_IP}:8000/api/claims"
echo -e "  open http://${ECS_PUBLIC_IP}:3010 in browser"
