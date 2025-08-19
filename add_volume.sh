#!/bin/bash
# Railway CLI commands to add a volume

# Install Railway CLI if not installed
# npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Add a volume to your service
railway volume add --mount /app/media --name media-volume

# Deploy with the volume
railway up