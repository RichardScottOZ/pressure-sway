# Getting Notifications for Pressure Changes

This guide shows you different ways to receive notifications when barometric pressure drops are detected.

> 💡 **Quick Answer:** Yes, GitHub can send email notifications without Gmail or any third-party service! See [GITHUB_NATIVE_NOTIFICATIONS.md](GITHUB_NATIVE_NOTIFICATIONS.md) for details.

## Option 1: GitHub Native Email Notifications (FREE - No Setup Required - RECOMMENDED)

**GitHub automatically sends email notifications for workflow failures to your GitHub notification email.** This is completely free and requires **zero configuration**. 

### How It Works

- GitHub sends emails to the address you use for GitHub notifications (check Settings → Notifications)
- You'll receive emails when:
  - The workflow fails (e.g., network issues, script errors)
  - The workflow job fails or is cancelled
- **No setup required** - works immediately for repository owners and watchers
- Goes to the same email you receive other GitHub notifications at

### What You Get

✅ **Free** - No third-party services needed  
✅ **Zero configuration** - Works out of the box  
✅ **Standard GitHub notifications** - Same format as other GitHub emails  
✅ **Reliable** - Managed by GitHub's infrastructure  

### Limitations

⚠️ GitHub's native notifications only alert on **workflow failures**, not on custom alerts like pressure drops. For pressure drop alerts, see Option 2 below.

### Configure Your GitHub Notification Email

1. Go to GitHub Settings: https://github.com/settings/notifications
2. Verify your notification email address
3. Ensure "Actions" notifications are enabled (should be on by default)
4. Done! You'll now receive emails when workflows fail

### Testing

1. Go to your repository's Actions tab
2. Manually run the workflow
3. If it fails, you'll receive an email notification automatically

---

## Option 2: Custom Email Notifications via Gmail (For Pressure Drop Alerts)

**Use this option if you want email notifications for pressure drop alerts in addition to workflow failures.**

### Setup Email Notifications

To receive custom email notifications for pressure drops, you need to configure Gmail app-specific password:

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

## Option 3: Alternative Email Providers (For Custom Alerts)

If you prefer not to use Gmail for custom pressure drop alerts, you can use other email providers by modifying the workflow secrets:

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

## Option 4: Slack Notifications

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

## Option 5: Discord Notifications

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

## Option 6: Custom Webhook

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

## Option 7: SMS Notifications (via Twilio)

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

## Option 8: Push Notifications (via Pushover)

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

**For most users, Option 1 (GitHub Native Notifications) is the best choice:**
- ✅ **Free** - No third-party services
- ✅ **Zero setup** - Works immediately
- ✅ **Reliable** - Uses GitHub's infrastructure
- ⚠️ **Limitation**: Only alerts on workflow failures, not pressure drops

**If you also want pressure drop alerts:**
- Use **Option 1** for workflow failures (free, no setup)
- Add **Option 2** (Gmail) for pressure drop alerts (requires setup)

**Other options:**
- **Best mobile experience**: Option 8 (Pushover) - one-time payment
- **Team notifications**: Option 4 (Slack) or Option 5 (Discord)
- **Immediate alerts**: Option 7 (SMS) - costs per message
