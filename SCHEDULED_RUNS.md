# Understanding GitHub Actions Scheduled Workflows

This document explains how scheduled workflows work in GitHub Actions and why your workflow might not run at the expected time.

## How Scheduled Workflows Work

The workflow is configured to run every hour using this cron expression:

```yaml
schedule:
  - cron: '0 * * * *'
```

This means: "Run at minute 0 of every hour" (00:00, 01:00, 02:00, etc.) in **UTC timezone**.

## Why Scheduled Runs Might Not Work

GitHub Actions has several requirements and limitations for scheduled workflows:

### 1. Default Branch Requirement

✅ **Required**: The workflow file MUST be in the default branch (main or master).

- Workflows in other branches will NOT run on schedule
- They can only be triggered manually or by events on those branches
- **Your workflow is now correctly in the main branch**

### 2. Repository Activity Requirement

⚠️ **Important**: GitHub automatically disables scheduled workflows after **60 days of repository inactivity**.

What counts as activity:
- Commits or pushes to the repository
- Manually running workflows
- Opening pull requests
- Creating issues

What GitHub does when inactive:
- Sends an email notification before disabling
- Disables the scheduled trigger (workflow still exists)
- You can re-enable by making any commit or manually running the workflow

### 3. Timing and Delays

⏰ **Expect delays**: Scheduled workflows don't run exactly on time.

- GitHub Actions queues scheduled workflows
- During high load periods, delays can be 5-15 minutes (or more)
- This is normal and expected behavior
- Don't rely on scheduled workflows for time-critical operations

### 4. First Run After Setup

🕐 **First scheduled run**: May take up to 1-2 hours after the workflow is added to the default branch.

Why:
- GitHub needs to index the workflow file
- The schedule is set up in the system
- Background processes need to register the cron job

What to do:
- Be patient after first setup
- Manually trigger the workflow once to test it
- Check back after the next scheduled time (at the top of the hour)

## Checking If Your Scheduled Workflow Is Active

### Method 1: GitHub Actions Tab

1. Go to your repository
2. Click on **Actions** tab
3. Look for runs with the event type "schedule"
4. If you see recent scheduled runs, it's working!

### Method 2: Check Workflow File

1. Ensure `.github/workflows/pressure_check.yml` exists in the main/master branch
2. Verify the cron syntax is correct: `'0 * * * *'`
3. Make sure there are no YAML syntax errors

### Method 3: Repository Insights

1. Go to **Insights** → **Traffic** (if you have access)
2. Recent activity indicates the repository is active
3. No activity for 60+ days means scheduled workflows might be disabled

## How to Keep Scheduled Workflows Active

### Option 1: Regular Manual Triggers

Every few weeks:
1. Go to **Actions** tab
2. Select "Barometric Pressure Check"
3. Click "Run workflow"

This counts as activity and resets the inactivity timer.

### Option 2: Automated Commits (Advanced)

You could set up a secondary workflow that makes automatic commits, but this is generally not recommended as it clutters the repository history.

### Option 3: Monitor and React

1. Watch for GitHub's warning email about inactive workflows
2. When you receive it, make a small commit or manual run
3. This re-enables the scheduled workflow

## Troubleshooting Scheduled Runs

### Issue: "My workflow hasn't run in the last hour"

**Check:**
1. What is the current UTC time? (`date -u` command or use a world clock)
2. Has it been at least 10-15 minutes past the hour? (GitHub may delay)
3. Is the workflow file in the main/master branch?
4. Has there been repository activity in the last 60 days?

**Solutions:**
- Wait a bit longer for GitHub's queue to process
- Manually trigger the workflow to test functionality
- Check the Actions tab for any error messages

### Issue: "Workflow runs on push but not on schedule"

This is the most common issue. **Causes:**

1. **Repository inactivity**: Make a commit or manual run
2. **New repository**: Wait 1-2 hours for GitHub to set up the schedule
3. **Wrong branch**: Ensure workflow is in the default branch

**Solution:**
Make any commit to the main branch or manually run the workflow once. Then wait for the next scheduled time.

### Issue: "I receive no notification even though the workflow runs"

**Check:**
1. Are the GitHub Secrets configured? (EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_TO)
2. Did the workflow detect any pressure drops? (Check logs)
3. Are there errors in the email notification steps? (Check workflow logs)

**Solution:**
See `SETUP_NOTIFICATIONS.md` for detailed setup instructions.

## Understanding the Cron Expression

```
'0 * * * *'
 │ │ │ │ │
 │ │ │ │ └─── Day of week (0-6, Sunday-Saturday)
 │ │ │ └───── Month (1-12)
 │ │ └─────── Day of month (1-31)
 │ └───────── Hour (0-23)
 └─────────── Minute (0-59)
```

Current setting: `'0 * * * *'`
- Minute: 0 (top of the hour)
- Hour: * (every hour)
- Day of month: * (every day)
- Month: * (every month)
- Day of week: * (every day of the week)

**Result**: Runs every hour at :00 minutes (UTC)

### Time Zone Note

⚠️ **All cron schedules use UTC time, not your local time.**

If you're in:
- **EST (UTC-5)**: Workflow runs at 7:00 PM, 8:00 PM, 9:00 PM... local time
- **PST (UTC-8)**: Workflow runs at 4:00 PM, 5:00 PM, 6:00 PM... local time
- **AEST (UTC+10)**: Workflow runs at 10:00 AM, 11:00 AM, 12:00 PM... local time
- **ACST (UTC+9:30)**: Workflow runs at 9:30 AM, 10:30 AM, 11:30 AM... local time

To convert UTC to your local time:
- Find your timezone offset from UTC
- Add/subtract from the hour in the cron expression
- Remember: The workflow still uses UTC internally

### Changing the Schedule

To run at different intervals, edit the cron expression in `.github/workflows/pressure_check.yml`:

```yaml
# Every 30 minutes
- cron: '*/30 * * * *'

# Every 2 hours
- cron: '0 */2 * * *'

# Every 6 hours (at 00:00, 06:00, 12:00, 18:00 UTC)
- cron: '0 0,6,12,18 * * *'

# Once a day at 9:00 AM UTC
- cron: '0 9 * * *'

# Twice a day at 8:00 AM and 8:00 PM UTC
- cron: '0 8,20 * * *'
```

**Note**: More frequent runs consume more GitHub Actions minutes, though you're unlikely to hit limits with this lightweight script.

## Best Practices

1. **Don't rely on exact timing** - Allow for 15-20 minute delays
2. **Keep repository active** - Make occasional commits or manual runs
3. **Monitor the Actions tab** - Check for failed runs regularly
4. **Set up notifications** - Get emails when issues occur
5. **Test manually first** - Use workflow_dispatch to verify everything works

## GitHub Actions Quotas

**Free tier limits** (per month):
- Public repositories: Unlimited minutes
- Private repositories: 2,000 minutes

**Your usage** (approximate):
- Each run: ~30 seconds
- Hourly runs: 24 runs/day
- Monthly: 720 runs × 0.5 minutes = 360 minutes

✅ Well within free tier limits, even for private repositories!

## Further Reading

- [GitHub Actions scheduled events documentation](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)
- [Cron syntax reference](https://crontab.guru/)
- [GitHub Actions usage limits](https://docs.github.com/en/actions/learn-github-actions/usage-limits-billing-and-administration)

## Summary

Your scheduled workflow should now work, but remember:
- ✅ Workflow is in the default branch
- ⏰ Runs every hour at :00 (UTC) with possible delays
- 📧 Email notifications are configured (after you set up secrets)
- 🔄 Needs occasional activity to stay enabled (every 60 days)
- 🧪 Can be manually triggered anytime for testing

If you continue to have issues, check the GitHub Actions tab for error messages or create an issue with details about what's not working.
