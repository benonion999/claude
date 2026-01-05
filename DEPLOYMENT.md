# Deployment Guide - Stock Picker Web Dashboard

This guide will help you deploy the Stock Picker web dashboard to a live URL using Render.com (free tier).

## Quick Deploy to Render.com

### Prerequisites

- A GitHub account
- Your code pushed to a GitHub repository

### Step-by-Step Deployment

1. **Push your code to GitHub** (if not already done)
   ```bash
   git push origin claude/stock-picker-alerts-H0w6N
   ```

2. **Sign up for Render.com**
   - Go to https://render.com
   - Sign up with your GitHub account (easiest option)

3. **Create a New Web Service**
   - Click "New +" button in the top right
   - Select "Web Service"
   - Connect your GitHub repository
   - Select the repository containing your Stock Picker code
   - Select the branch: `claude/stock-picker-alerts-H0w6N`

4. **Configure the Service**

   Fill in the following settings:

   - **Name**: `stock-picker` (or your preferred name)
   - **Region**: Choose closest to you (e.g., Oregon, Frankfurt)
   - **Branch**: `claude/stock-picker-alerts-H0w6N`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```
     gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT web_app:app
     ```
   - **Plan**: Select `Free` (or choose a paid plan for better performance)

5. **Environment Variables** (Optional)

   If you need to set custom environment variables, add them in the "Environment" section:
   - No special environment variables required for basic setup

6. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - This may take 5-10 minutes for the first deployment

7. **Access Your App**
   - Once deployed, you'll see your live URL at the top of the page
   - It will be something like: `https://stock-picker-xxxx.onrender.com`
   - Click the URL to access your Stock Picker dashboard!

## Alternative: Deploy Using render.yaml

If you want to use Infrastructure as Code:

1. Push your code to GitHub (including the `render.yaml` file)

2. In Render.com dashboard:
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will automatically detect `render.yaml` and configure everything

## Post-Deployment

### First-Time Setup

1. Visit your live URL: `https://your-app-name.onrender.com`

2. Click "Refresh Analysis" to load initial stock data

3. Navigate to Settings (`/settings`) to configure your stocks and parameters

### Important Notes

- **Free Tier Limitations**:
  - App spins down after 15 minutes of inactivity
  - First request after inactivity may take 30-60 seconds (cold start)
  - 750 hours/month of runtime (sufficient for most personal use)

- **Data Persistence**:
  - Configuration is saved in `config.json`
  - On free tier, filesystem is ephemeral (resets on redeploy)
  - Consider using environment variables for permanent config

- **Performance**:
  - Stock data fetching may be slower on free tier
  - Consider upgrading to paid plan for production use

### Monitoring

- View logs in Render dashboard under "Logs" tab
- Monitor app status and restart if needed
- Check deployment history

## Troubleshooting

### App Won't Start

- Check the build logs for errors
- Verify `requirements.txt` has all dependencies
- Ensure Python version compatibility

### WebSocket Issues

- Render free tier supports WebSockets
- If connections drop, check logs for errors
- Verify CORS settings in `web_app.py`

### Stock Data Not Loading

- Check API rate limits (yfinance)
- Verify internet connectivity from Render
- Check logs for specific error messages

### Configuration Not Persisting

- Free tier has ephemeral storage
- Use environment variables or external config storage
- Or upgrade to a paid plan with persistent disk

## Alternative Deployment Platforms

### Railway.app

1. Sign up at https://railway.app
2. Create new project from GitHub repo
3. Add these environment variables:
   - `PORT=5000` (Railway sets this automatically)
4. Railway will auto-detect Python and deploy

### Fly.io

1. Install Fly CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Login: `flyctl auth login`
3. Launch: `flyctl launch`
4. Deploy: `flyctl deploy`

### Heroku

1. Install Heroku CLI
2. Create Procfile:
   ```
   web: gunicorn --worker-class eventlet -w 1 web_app:app
   ```
3. Deploy:
   ```bash
   heroku create stock-picker-app
   git push heroku main
   ```

## Upgrading for Production

For production use, consider:

1. **Paid Hosting Plan**
   - Persistent storage
   - No sleep/cold starts
   - Better performance

2. **Database Integration**
   - Store historical data
   - Track recommendations over time
   - User authentication

3. **Caching**
   - Redis for stock data caching
   - Reduce API calls

4. **Monitoring**
   - Error tracking (Sentry)
   - Performance monitoring
   - Uptime monitoring

5. **Security**
   - Environment variables for secrets
   - Rate limiting
   - HTTPS (enabled by default on Render)

## Support

If you encounter issues:
- Check Render status page: https://status.render.com
- Review Render documentation: https://render.com/docs
- Check application logs in Render dashboard
