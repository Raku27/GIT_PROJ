#!/bin/bash

# GitHub Repository Setup Script
# Replace YOUR_GITHUB_USERNAME and YOUR_REPO_NAME with your actual values

GITHUB_USERNAME="Raku27"
REPO_NAME="GIT_PROJ"

echo "Setting up GitHub connection..."
echo "Make sure you've created the repository on GitHub first!"
echo ""

# Add remote origin
git remote add origin https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git

# Set main branch
git branch -M main

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Successfully connected to GitHub!"
echo "Your repository is now available at: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
