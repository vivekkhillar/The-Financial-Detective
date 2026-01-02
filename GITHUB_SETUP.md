# GitHub Setup Guide

This guide will help you connect your project to GitHub.

## Step 1: Install Git

If Git is not installed on your system, download and install it:

1. **Download Git for Windows**: Visit https://git-scm.com/download/win
2. **Run the installer** and follow the setup wizard
3. **Restart your terminal/IDE** after installation

## Step 2: Configure Git (First Time Only)

Open PowerShell or Command Prompt and run:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Replace with your actual name and email (preferably the one associated with your GitHub account).

## Step 3: Initialize Git Repository

Navigate to your project directory and run:

```bash
cd "C:\Users\vivek.khillar\OneDrive - Reliance Corporate IT Park Limited\Desktop\Hackathon\The Financial Detective"
git init
```

## Step 4: Create a GitHub Repository

1. Go to https://github.com and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Name your repository (e.g., "The-Financial-Detective")
5. Choose **Public** or **Private**
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click **"Create repository"**

## Step 5: Connect Local Repository to GitHub

After creating the repository on GitHub, you'll see instructions. Run these commands:

```bash
# Add all files to staging
git add .

# Create initial commit
git commit -m "Initial commit: Financial Detective project"

# Add remote repository (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note**: You may be prompted for your GitHub username and password. For security, GitHub now requires a Personal Access Token instead of a password.

### Creating a Personal Access Token:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click **"Generate new token (classic)"**
3. Give it a name (e.g., "Financial Detective")
4. Select scopes: **repo** (full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)
7. Use this token as your password when pushing

## Step 6: Verify Connection

Visit your GitHub repository URL to see your code online!

## Quick Commands Reference

```bash
# Check status
git status

# Add files
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push

# Pull from GitHub
git pull
```

## Troubleshooting

- **"git is not recognized"**: Make sure Git is installed and you've restarted your terminal
- **Authentication failed**: Use a Personal Access Token instead of password
- **Remote already exists**: Run `git remote remove origin` then add it again

