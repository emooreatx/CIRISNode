#!/bin/bash
# Script to catch up your fork's main branch to the latest main from upstream (CIRISAI/CIRISNode)
# Usage: ./git_catchup_main.sh

set -e

# Add upstream if not present
git remote get-url upstream > /dev/null 2>&1 || git remote add upstream https://github.com/CIRISAI/CIRISNode.git

echo "Fetching latest changes from upstream..."
git fetch upstream

echo "Checking out main branch..."
git checkout main

echo "Merging upstream/main into your local main..."
git merge upstream/main

echo "Pushing updated main to your fork (origin)..."
git push origin main

echo "Your fork's main is now up to date with upstream/main."
