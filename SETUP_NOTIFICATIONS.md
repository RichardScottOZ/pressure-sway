# Quick Setup Guide for Email Notifications

## TL;DR - Zero Setup Option (Recommended)

**GitHub already sends you email notifications for workflow failures!** No setup required.

- Goes to your GitHub notification email address
- Works immediately for workflow failures
- Completely free, no configuration needed
- Check/configure your email at: https://github.com/settings/notifications

**The setup guide below is ONLY needed if you want custom email alerts for pressure drops.**

---

## Custom Pressure Drop Email Setup (Optional)

This guide will help you set up custom email notifications for pressure drops in under 5 minutes.

### Prerequisites

- A Gmail account (or other email provider)
- Access to your GitHub repository settings

## Step-by-Step Setup

### Why This Setup?

This optional setup allows you to receive **custom email alerts for pressure drops** in addition to GitHub's native workflow failure notifications. If you only want to know when the workflow fails (not specific pressure drops), you don't need this setup.

### Step 1: Enable 2-Factor Authentication on Gmail

1. Go to your Google Account: https://myaccount.google.com/
2. Select **Security** from the menu
3. Under "Signing in to Google," select **2-Step Verification**
4. Follow the prompts to enable 2FA (if not already enabled)

### Step 2: Generate Gmail App-Specific Password

1. Go to: https://myaccount.google.com/apppasswords
2. You may need to sign in again
3. Under "Select app" choose **Mail**
4. Under "Select device" choose **Other** and enter "GitHub Pressure Monitor"
5. Click **Generate**
6. **Copy the 16-character password** that appears (you won't be able to see it again)

### Step 3: Add Secrets to GitHub Repository

1. Go to your repository on GitHub
2. Click on **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click the **New repository secret** button
5. Add the following three secrets one by one:

   **Secret 1:**
   - Name: `EMAIL_USERNAME`
   - Value: Your full Gmail address (e.g., `your.email@gmail.com`)
   - Click **Add secret**

   **Secret 2:**
   - Name: `EMAIL_PASSWORD`
   - Value: The 16-character app-specific password you generated
   - Click **Add secret**

   **Secret 3:**
   - Name: `EMAIL_TO`
   - Value: Email address where you want to receive alerts (can be the same as EMAIL_USERNAME)
   - Click **Add secret**

### Step 4: Test the Setup

1. Go to the **Actions** tab in your repository
2. Click on **"Barometric Pressure Check"** workflow
3. Click the **"Run workflow"** dropdown button (on the right)
4. Click the green **"Run workflow"** button
5. Wait 30-60 seconds for the workflow to complete
6. Check your email (and spam folder) for notifications

## What You'll Receive

Once configured, you'll automatically receive emails for:

- ⚠️ **Pressure Drop Alerts**: When barometric pressure drops significantly
- ❌ **Workflow Failures**: When the monitoring script fails to run

## Troubleshooting

### Not receiving emails?

1. **Check spam/junk folder** - emails might be filtered
2. **Verify secrets are correct**:
   - Go to Settings → Secrets and variables → Actions
   - Ensure all three secrets exist (you can't view values, but you can see if they're set)
   - If unsure, delete and re-add them
3. **Confirm 2FA is enabled** on your Google account
4. **Check workflow logs**:
   - Go to Actions tab
   - Click on a completed workflow run
   - Look for any errors in the email notification steps

### App-specific password not working?

- Make sure you're using the **app-specific password**, NOT your regular Gmail password
- The password should be 16 characters with no spaces
- If it's not working, generate a new one and update the secret

### Still having issues?

Check the workflow run logs:
1. Go to **Actions** tab
2. Click on the most recent workflow run
3. Expand the "Send email notification" steps
4. Look for error messages

Common issues:
- **Authentication failed**: Wrong password or username
- **Connection timeout**: SMTP port might be blocked (rare)
- **Recipient rejected**: Check EMAIL_TO is a valid email address

## Security Notes

- ✅ GitHub Secrets are encrypted and not visible once saved
- ✅ App-specific passwords are safer than your main Gmail password
- ✅ You can revoke app-specific passwords anytime from your Google Account
- ✅ Never commit secrets directly in code or workflow files

## Next Steps

- Wait for the hourly schedule to run automatically (every hour at :00 UTC)
- Monitor the Actions tab to see scheduled runs
- Adjust the pressure threshold in `config.json` if needed
- Review NOTIFICATIONS.md for alternative notification methods (Slack, Discord, etc.)

## Support

If you continue to have issues:
1. Check the workflow file: `.github/workflows/pressure_check.yml`
2. Review the complete documentation in `NOTIFICATIONS.md`
3. Create an issue on GitHub with the error messages from the workflow logs
