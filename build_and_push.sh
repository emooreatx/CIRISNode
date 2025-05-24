#!/bin/bash
# Build and push CIRISNode Docker images for backend, worker, and UI
# Usage: ./build_and_push.sh <dockerhub-username> <tag>
# Example: ./build_and_push.sh alignordie latest

set -e

if [ $# -ne 2 ]; then
  echo "Usage: $0 <dockerhub-username> <tag>"
  exit 1
fi

DOCKERHUB_USER="$1"
TAG="$2"

# Build backend image

echo "Building backend image..."
docker build -t "$DOCKERHUB_USER/cirisnode:backend-$TAG" -f Dockerfile .

echo "Pushing backend image..."
docker push "$DOCKERHUB_USER/cirisnode:backend-$TAG"

# Build worker image (same as backend, but with different tag if needed)
# If worker uses the same image, you can skip this or tag the same image

echo "Tagging worker image..."
docker tag "$DOCKERHUB_USER/cirisnode:backend-$TAG" "$DOCKERHUB_USER/cirisnode:worker-$TAG"
docker push "$DOCKERHUB_USER/cirisnode:worker-$TAG"

# Build UI image
if [ -d "ui" ]; then
  echo "Building UI image..."
  docker build -t "$DOCKERHUB_USER/cirisnode:ui-$TAG" -f ui/Dockerfile ui
  echo "Pushing UI image..."
  docker push "$DOCKERHUB_USER/cirisnode:ui-$TAG"
else
  echo "UI directory not found, skipping UI image build."
fi

echo "All images built and pushed with tag: $TAG"
