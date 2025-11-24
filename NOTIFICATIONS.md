# Getting Notifications for Pressure Changes

This guide shows you different ways to receive notifications when barometric pressure drops are detected.

## Option 1: GitHub Actions Email Notifications (Configured - Recommended)

**UPDATE**: The workflow has been updated to automatically send email notifications for both pressure drops and workflow failures. Follow the setup below to enable it.

### Setup Email Notifications

To receive email notifications, you need to configure Gmail app-specific password:

1. **Enable 2-factor authentication on your Google account** (required)
2. **Generate an app-specific password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" as the app
   - Generate the password and copy it

3. **Add secrets to your GitHub repository**:
   - Go to your repository on GitHub
   - Navigate to **Settings → Secrets and variables → Actions**
   - Click **New repository secret** and add these three secrets:
     - `EMAIL_USERNAME`: Your full Gmail address (e.g., your.email@gmail.com)
     - `EMAIL_PASSWORD`: The app-specific password you just generated (NOT your regular Gmail password)
     - `EMAIL_TO`: The email address where you want to receive alerts (can be the same as EMAIL_USERNAME)

### What You'll Receive

Once configured, you'll automatically receive emails for:
- **Pressure Drop Alerts**: When significant barometric pressure drops are detected
- **Workflow Failures**: When the monitoring workflow fails to run

### Testing Your Setup

After configuring the secrets:
1. Go to **Actions** tab in your repository
2. Select **"Barometric Pressure Check"** workflow
3. Click **"Run workflow"** button to manually trigger it
4. Wait for completion - you should receive an email if any alerts are detected

### Troubleshooting

If you don't receive emails:
- Verify all three secrets are set correctly (no extra spaces)
- Check your spam/junk folder
- Ensure 2FA is enabled on your Google account
- Make sure the app-specific password was generated correctly
- Check the workflow logs for any email sending errors

## Option 2: Alternative Email Providers

If you prefer not to use Gmail, you can use other email providers by modifying the workflow secrets:

### Using Other SMTP Providers

The workflow uses standard SMTP, so you can configure it with:
- **Outlook/Hotmail**: server_address: smtp.office365.com, port: 587
- **Yahoo Mail**: server_address: smtp.mail.yahoo.com, port: 587
- **SendGrid**: server_address: smtp.sendgrid.net, port: 587
- **Custom SMTP**: Use your own SMTP server settings

To use a different provider:
1. Update the workflow file `.github/workflows/pressure_check.yml`
2. Change `server_address` and `server_port` in both email notification steps
3. Use appropriate credentials in your GitHub secrets

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
