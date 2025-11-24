# pressure-sway
Barometric Pressure Monitor for BOM (Bureau of Meteorology) Australia

## Overview

This application monitors barometric pressure from the Australian Bureau of Meteorology website and alerts when significant pressure drops are detected. Pressure drops can indicate approaching weather changes, storms, or other meteorological events.

## Features

- 🌡️ Fetches real-time barometric pressure data from BOM website
- 📊 Compares current readings with previous readings
- ⚠️ Detects and logs pressure drops based on configurable threshold
- 💾 Persists data between runs for comparison
- 📝 Comprehensive logging with timestamps
- ⏰ Runs automatically on schedule via GitHub Actions (free)
- 🔧 Fully configurable via JSON config file

## How It Works

1. The script fetches the BOM observation page
2. Parses the HTML to extract barometric pressure (in hPa)
3. Compares with the last recorded reading
4. If pressure has dropped by more than the threshold, logs a warning
5. Saves the current reading for next comparison
6. GitHub Actions runs this every hour automatically

## Setup

### Local Usage

1. Clone the repository:
```bash
git clone https://github.com/RichardScottOZ/pressure-sway.git
cd pressure-sway
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure settings in `config.json` (optional):
```json
{
  "station_url": "https://www.bom.gov.au/products/IDS60901/IDS60901.94648.shtml",
  "pressure_drop_threshold_hpa": 2.0,
  "check_interval_minutes": 60,
  "data_file": "pressure_data.json",
  "log_file": "pressure_monitor.log"
}
```

4. Run the monitor:
```bash
python pressure_monitor.py
```

### GitHub Actions (Automated)

The application is set up to run automatically in GitHub Actions:

- **Runs every hour** via scheduled cron job (at the top of each hour: 00:00, 01:00, 02:00, etc. UTC)
- **Zero cost** - runs on GitHub's free tier
- **Minimal resources** - uses ubuntu-latest runner
- **Persistent data** - uses GitHub Actions cache for storing last reading
- **Logs archived** - logs are saved as artifacts for 30 days
- **Email notifications** - get alerts for pressure drops and workflow failures

#### Enable GitHub Actions:

1. Fork or push this repository to GitHub
2. Go to the "Actions" tab in your repository
3. Enable workflows if prompted
4. The workflow will run automatically every hour

#### Important Notes for Scheduled Runs:

⚠️ **GitHub Actions scheduled workflows require**:
- The workflow file must be in the **default branch** (main or master)
- The repository should have **recent activity** (commits, pushes, or manual workflow runs)
- GitHub may **disable scheduled workflows** after 60 days of repository inactivity
- If disabled, make any commit or manually run the workflow to re-enable it
- Scheduled runs use **UTC timezone** and may have 5-15 minute delays

💡 **To keep schedules active**: 
- Manually trigger the workflow occasionally if no commits are being made
- GitHub will send a notification email if scheduled workflows are disabled due to inactivity

📖 **For detailed information about scheduled runs**, see [SCHEDULED_RUNS.md](SCHEDULED_RUNS.md)

#### Manual Trigger:

You can also trigger a check manually - **see [MANUAL_RUN.md](MANUAL_RUN.md)** for detailed instructions:
1. Go to Actions tab
2. Select "Barometric Pressure Check" workflow
3. Click "Run workflow"

#### Getting Notifications:

**Email notifications are now built into the workflow!** Just configure three GitHub secrets to enable them:
- `EMAIL_USERNAME` - Your Gmail address
- `EMAIL_PASSWORD` - Gmail app-specific password
- `EMAIL_TO` - Where to send alerts

See **[NOTIFICATIONS.md](NOTIFICATIONS.md)** for:
- **Email setup instructions** (Option 1 - Recommended)
- Alternative notification methods (Slack, Discord, SMS, Push notifications)
- Troubleshooting tips

## Configuration

Edit `config.json` to customize:

- `station_url`: BOM station observation page URL (find your local station at bom.gov.au)
- `pressure_drop_threshold_hpa`: Minimum pressure drop in hPa to trigger alert (default: 2.0)
- `check_interval_minutes`: How often to check (used for documentation, actual schedule in workflow)
- `data_file`: Where to store last reading
- `log_file`: Where to write logs

## BOM Station URLs

To monitor a different location:

1. Visit https://www.bom.gov.au/
2. Search for your location
3. Go to "Latest Weather Observations"
4. Copy the URL (format: `IDS60901/IDS60901.XXXXX.shtml`)
5. Update `station_url` in `config.json`

## Logs and Monitoring

- Logs are written to `pressure_monitor.log`
- In GitHub Actions, logs are uploaded as artifacts
- View logs in Actions tab → Select run → Download artifacts

## Understanding Pressure Changes

- **Rapid drop** (>2 hPa/hour): May indicate approaching storm or low-pressure system
- **Gradual drop**: General weather deterioration
- **Rising pressure**: Improving weather, clearing conditions
- **Steady pressure**: Stable weather conditions

## Cost and Resource Requirements

- **GitHub Actions**: FREE (2,000 minutes/month on free tier)
- **CPU**: Minimal (runs in seconds)
- **Memory**: <50MB
- **Storage**: Negligible (few KB for data and logs)
- **Network**: One HTTP request per run

This makes it extremely cost-effective and perfect for running 24/7.

## Alternative Deployment Options

### GitHub Codespaces
```bash
# Start a codespace, then:
while true; do python pressure_monitor.py; sleep 1800; done
```

### Heroku (Free Tier)
```bash
# Create Procfile:
echo "worker: while true; do python pressure_monitor.py; sleep 1800; done" > Procfile
```

### Cloud Functions (Scheduled)
- AWS Lambda + CloudWatch Events
- Google Cloud Functions + Cloud Scheduler
- Azure Functions + Timer Trigger

## Development

### Run Tests
```bash
# Test the script
python pressure_monitor.py
```

### Check Logs
```bash
tail -f pressure_monitor.log
```

## License

MIT License - feel free to use and modify

## Contributing

Pull requests welcome! Please ensure your changes:
- Maintain minimal resource usage
- Include appropriate error handling
- Update documentation as needed
