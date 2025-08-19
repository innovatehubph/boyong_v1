#!/bin/bash

# GitHub Push Script with Authentication
# Replace YOUR_GITHUB_TOKEN with your actual Personal Access Token

echo "🚀 Pushing Pareng Boyong to GitHub..."
echo ""
echo "You need to provide GitHub authentication."
echo ""
echo "📋 To get a Personal Access Token:"
echo "1. Go to GitHub.com → Settings → Developer settings → Personal access tokens"
echo "2. Click 'Generate new token (classic)'"
echo "3. Select 'repo' scope"
echo "4. Generate and copy the token"
echo ""
read -p "Enter your GitHub username: " GITHUB_USER
read -s -p "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
echo ""

# Set the remote URL with authentication
git remote set-url origin https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/innovatehubph/boyong_v1.git

# Push to GitHub
echo ""
echo "🔄 Pushing to GitHub..."
git push -u origin main

# Remove the token from the URL after push for security
git remote set-url origin https://github.com/innovatehubph/boyong_v1.git

echo ""
echo "✅ Push complete! Repository is now on GitHub."
echo "🌐 View at: https://github.com/innovatehubph/boyong_v1"