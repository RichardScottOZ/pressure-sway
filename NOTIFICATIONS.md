# Getting Notifications for Pressure Changes

This guide shows you different ways to receive notifications when barometric pressure drops are detected.

## Option 1: GitHub Actions Email Notifications (Easiest)

GitHub can email you when workflows fail or complete with warnings.

### Enable Email Notifications

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Click on a workflow run
4. Click "Watch" or configure in: **Settings → Notifications → Actions**

You'll receive emails when:
- Workflow fails (e.g., can't fetch data)
- Warnings are logged (pressure drops)

### Limitations
- Only notifies on workflow failures or completion
- Doesn't send real-time alerts for pressure drops mid-run

## Option 2: GitHub Actions with Email Action (Recommended)

Add email notifications directly to the workflow.

### Setup

1. Add email credentials to GitHub Secrets:
   - Go to **Settings → Secrets and variables → Actions**
   - Add these secrets:
     - `EMAIL_USERNAME`: Your Gmail address
     - `EMAIL_PASSWORD`: Gmail app-specific password (not your regular password)
     - `EMAIL_TO`: Email address to receive alerts

2. Update `.github/workflows/pressure_check.yml`:

Add this step after "Run pressure monitor":

```yaml
    - name: Check for pressure drop alerts
      id: check_alerts
      run: |
        if grep -q "PRESSURE DROP DETECTED" pressure_monitor.log; then
          echo "alert_found=true" >> $GITHUB_OUTPUT
          echo "ALERT_MESSAGE<<EOF" >> $GITHUB_OUTPUT
          grep -A 5 "PRESSURE DROP DETECTED" pressure_monitor.log | tail -6 >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
        fi

    - name: Send email notification
      if: steps.check_alerts.outputs.alert_found == 'true'
      uses: dawidd6/action-send-mail@v3
      with:
        server_address: smtp.gmail.com
        server_port: 587
        username: ${{ secrets.EMAIL_USERNAME }}
        password: ${{ secrets.EMAIL_PASSWORD }}
        subject: '⚠️ Barometric Pressure Drop Detected'
        to: ${{ secrets.EMAIL_TO }}
        from: Pressure Monitor
        body: |
          A significant barometric pressure drop has been detected:
          
          ${{ steps.check_alerts.outputs.ALERT_MESSAGE }}
          
          View full logs: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
```

### Gmail App-Specific Password

1. Enable 2-factor authentication on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use this password in `EMAIL_PASSWORD` secret

## Option 3: Slack Notifications

Send alerts to a Slack channel.

### Setup

1. Create a Slack Incoming Webhook:
   - Go to: https://api.slack.com/messaging/webhooks
   - Create a new webhook for your workspace
   - Copy the webhook URL

2. Add webhook to GitHub Secrets:
   - Go to **Settings → Secrets and variables → Actions**
   - Add secret: `SLACK_WEBHOOK_URL`

3. Add this step to `.github/workflows/pressure_check.yml`:

```yaml
    - name: Check for pressure drop alerts
      id: check_alerts
      run: |
        if grep -q "PRESSURE DROP DETECTED" pressure_monitor.log; then
          echo "alert_found=true" >> $GITHUB_OUTPUT
        fi

    - name: Send Slack notification
      if: steps.check_alerts.outputs.alert_found == 'true'
      uses: slackapi/slack-github-action@v1.26.0
      with:
        payload: |
          {
            "text": "⚠️ *Barometric Pressure Drop Detected*",
            "blocks": [
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "⚠️ *Barometric Pressure Drop Detected*\n\nA significant pressure drop has been detected. Check the logs for details:\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run Logs>"
                }
              }
            ]
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```

## Option 4: Discord Notifications

Send alerts to a Discord channel.

### Setup

1. Create a Discord Webhook:
   - Go to your Discord server settings
   - Select "Integrations" → "Webhooks"
   - Click "New Webhook"
   - Copy the webhook URL

2. Add webhook to GitHub Secrets:
   - Add secret: `DISCORD_WEBHOOK_URL`

3. Add this step to `.github/workflows/pressure_check.yml`:

```yaml
    - name: Send Discord notification
      if: steps.check_alerts.outputs.alert_found == 'true'
      run: |
        curl -H "Content-Type: application/json" \
             -d "{\"content\": \"⚠️ **Barometric Pressure Drop Detected**\n\nCheck logs: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}\"}" \
             ${{ secrets.DISCORD_WEBHOOK_URL }}
```

## Option 5: Custom Webhook

Send alerts to any custom webhook endpoint.

### Setup

1. Add your webhook URL to GitHub Secrets:
   - Add secret: `CUSTOM_WEBHOOK_URL`

2. Add this step to `.github/workflows/pressure_check.yml`:

```yaml
    - name: Send webhook notification
      if: steps.check_alerts.outputs.alert_found == 'true'
      run: |
        TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        curl -X POST ${{ secrets.CUSTOM_WEBHOOK_URL }} \
             -H "Content-Type: application/json" \
             -d "{
               \"event\": \"pressure_drop\",
               \"message\": \"Barometric pressure drop detected\",
               \"repository\": \"${{ github.repository }}\",
               \"run_id\": \"${{ github.run_id }}\",
               \"timestamp\": \"$TIMESTAMP\"
             }"
```

## Option 6: SMS Notifications (via Twilio)

Send SMS alerts using Twilio.

### Setup

1. Sign up for Twilio: https://www.twilio.com/
2. Get your Account SID, Auth Token, and a Twilio phone number
3. Add to GitHub Secrets:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_FROM`: Your Twilio phone number
   - `TWILIO_PHONE_TO`: Your mobile number

4. Add this step to `.github/workflows/pressure_check.yml`:

```yaml
    - name: Send SMS notification
      if: steps.check_alerts.outputs.alert_found == 'true'
      run: |
        curl -X POST "https://api.twilio.com/2010-04-01/Accounts/${{ secrets.TWILIO_ACCOUNT_SID }}/Messages.json" \
             --data-urlencode "From=${{ secrets.TWILIO_PHONE_FROM }}" \
             --data-urlencode "To=${{ secrets.TWILIO_PHONE_TO }}" \
             --data-urlencode "Body=⚠️ Barometric pressure drop detected! Check your pressure monitor." \
             -u "${{ secrets.TWILIO_ACCOUNT_SID }}:${{ secrets.TWILIO_AUTH_TOKEN }}"
```

Note: Twilio charges per SMS (typically $0.0075-$0.01 per message).

## Option 7: Push Notifications (via Pushover)

Send push notifications to your mobile device using Pushover.

### Setup

1. Sign up for Pushover: https://pushover.net/ ($5 one-time fee per platform)
2. Create an application and get your API token
3. Get your user key from the dashboard
4. Add to GitHub Secrets:
   - `PUSHOVER_TOKEN`: Your application API token
   - `PUSHOVER_USER`: Your user key

5. Add this step to `.github/workflows/pressure_check.yml`:

```yaml
    - name: Send push notification
      if: steps.check_alerts.outputs.alert_found == 'true'
      run: |
        curl -s \
             --form-string "token=${{ secrets.PUSHOVER_TOKEN }}" \
             --form-string "user=${{ secrets.PUSHOVER_USER }}" \
             --form-string "message=Barometric pressure drop detected! Check logs for details." \
             --form-string "title=⚠️ Pressure Alert" \
             --form-string "priority=1" \
             https://api.pushover.net/1/messages.json
```

## Testing Notifications

After setting up notifications, test them:

1. Manually trigger a workflow run:
   - Go to **Actions** tab
   - Select "Barometric Pressure Check"
   - Click "Run workflow"

2. Or temporarily lower the threshold to trigger alerts:
   - Edit `config.json`: `"pressure_drop_threshold_hpa": 0.1`
   - Commit and push

3. Check that you receive the notification through your chosen method

## Monitoring without Notifications

If you don't want active notifications, you can:

1. **Check Actions tab regularly**
   - View workflow runs
   - Download and review log artifacts

2. **Use GitHub Mobile App**
   - Get push notifications for workflow status
   - Available on iOS and Android

3. **RSS Feed**
   - Subscribe to your repository's releases/activity feed
   - Some RSS readers support push notifications

## Troubleshooting

### Not receiving email notifications
- Check spam/junk folder
- Verify Gmail app password is correct
- Ensure 2FA is enabled on Google account

### Slack/Discord webhook not working
- Verify webhook URL is correct
- Check webhook hasn't been deleted in Slack/Discord settings
- Test webhook manually with curl

### Workflow not detecting alerts
- Check `pressure_monitor.log` artifact to confirm alert was logged
- Verify the grep pattern matches your log format
- Ensure the "Check for pressure drop alerts" step runs before notification steps

## Recommendation

For most users, **Option 2 (Email)** or **Option 5 (Pushover)** work best:
- Email: Free, reliable, works everywhere
- Pushover: One-time payment, excellent mobile notifications

Choose based on:
- **Free + simple**: Email (Option 2)
- **Best mobile experience**: Pushover (Option 7)
- **Team notifications**: Slack (Option 3) or Discord (Option 4)
- **Immediate alerts**: SMS (Option 6) - but costs per message
