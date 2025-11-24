# Running the Pressure Monitor Manually

This guide explains how to run the pressure monitor manually, both online and offline.

## Running Manually Online (GitHub Actions)

You can trigger the pressure monitor to run immediately without waiting for the scheduled time.

### Method 1: GitHub Web Interface (Easiest)

1. **Go to your repository on GitHub**
   - Navigate to: `https://github.com/YOUR_USERNAME/pressure-sway`

2. **Click the "Actions" tab**
   - It's in the top menu bar of your repository

3. **Select the workflow**
   - Click "Barometric Pressure Check" in the left sidebar

4. **Trigger a manual run**
   - Click the "Run workflow" button (top right)
   - Select the branch (usually `main` or `master`)
   - Click the green "Run workflow" button

5. **Monitor the run**
   - The workflow will appear in the runs list
   - Click on it to see real-time progress
   - Wait for completion (usually takes 30-60 seconds)

6. **View results**
   - Logs are shown in each step
   - Download the log artifact for detailed output
   - Check for pressure drop alerts in the logs

### Method 2: GitHub CLI

If you have GitHub CLI installed:

```bash
# Install GitHub CLI first (if not installed)
# macOS: brew install gh
# Linux: See https://github.com/cli/cli#installation
# Windows: winget install GitHub.cli

# Authenticate
gh auth login

# Trigger workflow
gh workflow run "pressure_check.yml" --repo YOUR_USERNAME/pressure-sway

# View recent runs
gh run list --repo YOUR_USERNAME/pressure-sway --limit 5

# Watch the latest run
gh run watch --repo YOUR_USERNAME/pressure-sway
```

### Method 3: GitHub API

Using curl or any HTTP client:

```bash
# Get a personal access token from:
# https://github.com/settings/tokens
# Needs 'repo' and 'workflow' scopes

TOKEN="your_github_token"
OWNER="YOUR_USERNAME"
REPO="pressure-sway"

# Trigger workflow
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/workflows/pressure_check.yml/dispatches" \
  -d '{"ref":"main"}'

# Check run status
curl -H "Accept: application/vnd.github+json" \
     -H "Authorization: Bearer $TOKEN" \
     "https://api.github.com/repos/$OWNER/$REPO/actions/runs?per_page=1"
```

### When to Use Manual Online Runs

- **Testing**: After changing configuration or code
- **Immediate check**: Want to check pressure right now
- **Debugging**: Troubleshooting issues with the workflow
- **On-demand**: Before going outdoors or planning activities

## Running Manually Offline (Local Computer)

Run the pressure monitor on your own computer without GitHub.

### Prerequisites

1. **Python 3.8 or higher**
   ```bash
   python3 --version
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/pressure-sway.git
   cd pressure-sway
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or with pip3:
   pip3 install -r requirements.txt
   ```

### Single Run

Run the monitor once:

```bash
python3 pressure_monitor.py
```

**Output example:**
```
2024-11-24 10:30:00 - INFO - ============================================================
2024-11-24 10:30:00 - INFO - Starting pressure check
2024-11-24 10:30:00 - INFO - Fetching data from https://www.bom.gov.au/...
2024-11-24 10:30:01 - INFO - Successfully parsed pressure: 1013.2 hPa
2024-11-24 10:30:01 - INFO - Pressure change: +0.50 hPa (Previous: 1012.7, Current: 1013.2)
2024-11-24 10:30:01 - INFO - Pressure check completed
2024-11-24 10:30:01 - INFO - ============================================================
```

**Files created:**
- `pressure_data.json`: Stores current reading for next comparison
- `pressure_monitor.log`: Detailed logs

### Continuous Monitoring (Keep Running)

Run continuously with automatic checks:

```bash
./run_monitor.sh
```

This will:
- Run the monitor every hour (configurable)
- Keep running until you stop it (Ctrl+C)
- Log all output to file and console

**Customize interval:**
```bash
# Check every 30 minutes (1800 seconds)
CHECK_INTERVAL=1800 ./run_monitor.sh

# Check every 15 minutes
CHECK_INTERVAL=900 ./run_monitor.sh

# Check every 2 hours
CHECK_INTERVAL=7200 ./run_monitor.sh
```

### Running in the Background

**On macOS/Linux:**
```bash
# Start in background
nohup ./run_monitor.sh > monitor.out 2>&1 &

# Check if running
ps aux | grep pressure_monitor

# Stop it
pkill -f pressure_monitor.py
```

**On Windows (PowerShell):**
```powershell
# Start in background
Start-Process python -ArgumentList "pressure_monitor.py" -NoNewWindow -PassThru

# Or use Task Scheduler for recurring runs
```

## Running in GitHub Codespaces (Online but in a Terminal)

GitHub Codespaces provides a cloud development environment.

### Setup

1. **Open repository in Codespaces**
   - Go to your repository on GitHub
   - Click "Code" button → "Codespaces" tab
   - Click "Create codespace on main"

2. **Wait for environment to load**
   - Codespaces will automatically install dependencies
   - Terminal will open automatically

3. **Run the monitor**
   ```bash
   python3 pressure_monitor.py
   ```

4. **For continuous monitoring**
   ```bash
   ./run_monitor.sh
   ```

### Codespaces Considerations

- **Free tier**: 60 hours/month for free
- **Auto-shutdown**: Idle after 30 minutes (configurable)
- **Not ideal for 24/7**: Better for testing and development
- **Recommendation**: Use GitHub Actions for automatic monitoring, Codespaces for testing

## Running with Docker (Offline or Online)

### Build and Run

```bash
# Build the image
docker build -t pressure-monitor .

# Run once
docker run --rm -v $(pwd)/data:/app/data pressure-monitor

# Run continuously in background
docker run -d \
  --name pressure-monitor \
  --restart unless-stopped \
  -v $(pwd)/data:/app/data \
  pressure-monitor

# View logs
docker logs -f pressure-monitor

# Stop
docker stop pressure-monitor
docker rm pressure-monitor
```

### Run on Cloud (Online)

Deploy to any Docker-compatible platform:

**AWS ECS/Fargate:**
```bash
# Push to ECR
aws ecr create-repository --repository-name pressure-monitor
docker tag pressure-monitor:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/pressure-monitor
docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/pressure-monitor

# Create task definition and service via AWS Console
```

**Google Cloud Run:**
```bash
gcloud run deploy pressure-monitor \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Azure Container Instances:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name pressure-monitor \
  --image pressure-monitor:latest \
  --restart-policy Always
```

## Running on Raspberry Pi (Offline, Always On)

Perfect for a local always-on monitor:

```bash
# On Raspberry Pi
git clone https://github.com/YOUR_USERNAME/pressure-sway.git
cd pressure-sway
pip3 install -r requirements.txt

# Test run
python3 pressure_monitor.py

# Set up systemd service for automatic startup
sudo nano /etc/systemd/system/pressure-monitor.service
```

**Service file content:**
```ini
[Unit]
Description=Barometric Pressure Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pressure-sway
ExecStart=/usr/bin/python3 /home/pi/pressure-sway/pressure_monitor.py
Restart=always
RestartSec=3600

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable pressure-monitor.service
sudo systemctl start pressure-monitor.service

# Check status
sudo systemctl status pressure-monitor.service

# View logs
sudo journalctl -u pressure-monitor.service -f
```

## Viewing Results

### After GitHub Actions Run

1. **Actions tab** → Select run → View logs
2. **Download artifacts** → `pressure-logs-XXX.zip`
3. **Extract and open** `pressure_monitor.log`

### After Local Run

```bash
# View latest logs
tail -f pressure_monitor.log

# View all logs
cat pressure_monitor.log

# View just pressure drops
grep "PRESSURE DROP DETECTED" pressure_monitor.log

# View current stored data
cat pressure_data.json
```

## Comparison: Online vs Offline

| Feature | GitHub Actions (Online) | Local (Offline) |
|---------|------------------------|-----------------|
| **Cost** | Free | Free (uses your electricity) |
| **Setup** | Click "Run workflow" | Install Python + dependencies |
| **Maintenance** | None | Keep computer running |
| **Reliability** | Very high (GitHub's infrastructure) | Depends on your setup |
| **Customization** | Edit workflow file | Full control |
| **Notifications** | Easy to add (see NOTIFICATIONS.md) | Need to implement |
| **Logs** | Stored in GitHub artifacts | Local files |
| **Best for** | Automated, hands-off monitoring | Testing, development, local control |

## Recommendations

### For Regular Monitoring
**Use GitHub Actions** - It's free, automated, and reliable. Just enable it once and forget about it.

### For Testing
**Use local/Codespaces** - Faster iteration when developing or debugging.

### For Immediate Check
**Manual GitHub Actions run** - Quick, no setup needed.

### For Complete Control
**Raspberry Pi with systemd** - Always on, fully under your control.

## Troubleshooting

### "ModuleNotFoundError" when running locally
```bash
pip3 install -r requirements.txt
# or
pip install -r requirements.txt
```

### Can't access BOM website locally
- Check internet connection
- Try different network (some networks block BOM)
- Use VPN if needed

### GitHub Actions manual run button missing
- Ensure `workflow_dispatch` is in the workflow file
- Refresh the page
- Check you have write permissions to the repository

### Workflow won't run manually
- Verify the workflow file syntax is valid
- Ensure workflow is enabled (check Actions settings)
- Branch name must match (main, master, etc.)

## Quick Reference

```bash
# GitHub (online, manual)
Actions tab → Run workflow → Click button

# Local (offline, once)
python3 pressure_monitor.py

# Local (offline, continuous)
./run_monitor.sh

# Codespaces (online terminal)
python3 pressure_monitor.py

# Docker (offline/online)
docker run --rm -v $(pwd)/data:/app/data pressure-monitor

# View logs
tail -f pressure_monitor.log
```
