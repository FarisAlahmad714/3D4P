# Railway Volume Setup for Media Files

Follow these steps to set up persistent storage for uploaded images on Railway:

## Step 1: Create a Volume in Railway Dashboard

1. Go to your Railway project dashboard
2. Click on your deployed service
3. Navigate to the "Settings" tab
4. Scroll down to the "Volumes" section
5. Click "Add Volume"
6. Configure the volume:
   - **Name**: media_volume
   - **Mount Path**: /app/media
   - **Size**: 1GB (or as needed)
7. Click "Deploy" to save the volume

## Step 2: Deploy the Updated Configuration

The code has been updated with:

1. **railway.toml** - Defines the volume mount configuration
2. **settings.py** - Updated to use `/app/media` path when running on Railway
3. **urls.py** - Ensures media files are served correctly

## Step 3: Verify the Setup

After deployment:

1. Test uploading an image through your application
2. Verify the image displays correctly
3. Trigger a redeploy through Railway dashboard
4. Check if the previously uploaded image is still accessible

## Important Notes

- The volume will persist data across deployments
- Initial deployment might take a moment to provision the volume
- Make sure the volume name in railway.toml matches the one created in dashboard
- Railway automatically sets the `RAILWAY_ENVIRONMENT` variable which the app uses to detect it's running on Railway

## Troubleshooting

If images aren't persisting:

1. Check Railway logs for any permission errors
2. Verify the volume is mounted at `/app/media`
3. Ensure the `RAILWAY_ENVIRONMENT` variable is set in Railway
4. Check that media files are being saved to the correct path

## Migration from Existing Media

If you have existing media files to migrate:

1. Download them from your old deployment
2. Upload them manually through your application
3. Or use Railway CLI to copy files directly to the volume