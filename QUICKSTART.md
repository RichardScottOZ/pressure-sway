# Quick Start Guide

## Fastest Way to Get Started (GitHub Actions)

1. **Fork or clone this repository to your GitHub account**

2. **Enable GitHub Actions**
   - Go to the "Actions" tab in your repository
   - Click "I understand my workflows, go ahead and enable them"

3. **That's it!** 
   - The monitor will automatically run every hour
   - Check the Actions tab to see runs and logs
   - Download logs as artifacts to review pressure data

4. **Optional: Set up notifications**
   - See [NOTIFICATIONS.md](NOTIFICATIONS.md) for email, Slack, SMS, and more

5. **Run manually anytime**
   - See [MANUAL_RUN.md](MANUAL_RUN.md) for instructions

## Run Locally (5 minutes)

```bash
# Clone the repository
git clone https://github.com/RichardScottOZ/pressure-sway.git
cd pressure-sway

# Install dependencies
pip install -r requirements.txt

# Run once
python pressure_monitor.py

# Run continuously (checks every hour by default)
./run_monitor.sh

# Or customize the interval (e.g., every 30 minutes)
CHECK_INTERVAL=1800 ./run_monitor.sh
```

## Run with Docker

```bash
# Build the image
docker build -t pressure-monitor .

# Run once
docker run --rm -v $(pwd)/data:/app/data pressure-monitor

# Run continuously
docker run -d --restart unless-stopped \
  -v $(pwd)/data:/app/data \
  --name pressure-monitor \
  pressure-monitor

# View logs
docker logs -f pressure-monitor
```

## Example Output

### First Run (No Previous Data)
```
2024-11-23 14:30:00 - INFO - ============================================================
2024-11-23 14:30:00 - INFO - Starting pressure check
2024-11-23 14:30:00 - INFO - Fetching data from https://www.bom.gov.au/...
2024-11-23 14:30:01 - INFO - Successfully parsed pressure: 1013.5 hPa
2024-11-23 14:30:01 - INFO - No previous reading available for comparison
2024-11-23 14:30:01 - INFO - Pressure check completed
2024-11-23 14:30:01 - INFO - ============================================================
```

### Pressure Drop Detected
```
2024-11-23 15:00:00 - INFO - ============================================================
2024-11-23 15:00:00 - INFO - Starting pressure check
2024-11-23 15:00:00 - INFO - Fetching data from https://www.bom.gov.au/...
2024-11-23 15:00:01 - INFO - Successfully parsed pressure: 1010.2 hPa
2024-11-23 15:00:01 - INFO - Pressure change: +3.30 hPa (Previous: 1013.5, Current: 1010.2)
2024-11-23 15:00:01 - WARNING - ⚠️  PRESSURE DROP DETECTED! ⚠️
  Previous: 1013.5 hPa at 2024-11-23T14:30:00
  Current:  1010.2 hPa at 2024-11-23T15:00:00
  Drop:     3.30 hPa (threshold: 2.0 hPa)
  This may indicate approaching weather change.
2024-11-23 15:00:01 - INFO - Pressure check completed
2024-11-23 15:00:01 - INFO - ============================================================
```

### Normal Reading
```
2024-11-23 15:30:00 - INFO - ============================================================
2024-11-23 15:30:00 - INFO - Starting pressure check
2024-11-23 15:30:00 - INFO - Fetching data from https://www.bom.gov.au/...
2024-11-23 15:30:01 - INFO - Successfully parsed pressure: 1010.5 hPa
2024-11-23 15:30:01 - INFO - Pressure change: -0.30 hPa (Previous: 1010.2, Current: 1010.5)
2024-11-23 15:30:01 - INFO - Pressure check completed
2024-11-23 15:30:01 - INFO - ============================================================
```

## Customization

Edit `config.json` to customize behavior:

```json
{
  "station_url": "https://www.bom.gov.au/products/IDS60901/IDS60901.94648.shtml",
  "pressure_drop_threshold_hpa": 2.0,
  "check_interval_minutes": 30,
  "data_file": "pressure_data.json",
  "log_file": "pressure_monitor.log"
}
```

**Common changes:**
- Change `station_url` to monitor a different location
- Adjust `pressure_drop_threshold_hpa` for more/less sensitive alerts
- Modify GitHub Actions workflow to change check frequency

## Finding Your Local Station

1. Visit https://www.bom.gov.au/
2. Search for your city/town
3. Click "Latest Weather Observations"
4. Copy the URL (looks like: `IDS60901/IDS60901.XXXXX.shtml`)
5. Update `station_url` in `config.json`

## Troubleshooting

### Script can't reach BOM website
- Check your internet connection
- Verify the station URL is correct
- Some networks may block BOM access

### No pressure data found
- The BOM page structure may have changed
- Try a different station URL
- Check the logs for specific error messages

### GitHub Actions not running
- Ensure workflows are enabled in repository settings
- Check the Actions tab for error messages
- Verify the workflow file syntax

## Cost Breakdown

**GitHub Actions (Recommended):**
- FREE for public repositories
- FREE for private repos (2,000 minutes/month)
- This app uses ~1 minute/month
- Storage for cache and artifacts: FREE (included)

**Running 24/7 for a year:**
- Cost: $0.00
- Resource usage: Negligible

## Next Steps

- Monitor the logs to understand pressure patterns in your area
- Adjust the threshold based on your local weather patterns
- Set up notifications (email, Slack, etc.) by extending the script
- Add multiple station monitoring by running multiple instances
