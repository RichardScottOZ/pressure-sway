# GitHub Native Email Notifications

## Yes, GitHub Can Send Email Notifications Without Third-Party Setup!

**GitHub Actions has built-in email notifications for workflow failures.** No Gmail, SendGrid, or any third-party email provider is needed.

## How It Works

GitHub automatically sends email notifications to:
- Repository owners
- Users who triggered the workflow
- Users watching the repository (with Actions notifications enabled)

**These notifications are sent to your GitHub notification email address.**

## What You Need to Do

### 1. Verify Your Notification Settings

1. Go to: https://github.com/settings/notifications
2. Make sure you have an email address configured
3. Ensure "Actions" notifications are enabled (they're on by default)
4. That's it!

### 2. Enable Notifications for This Repository

1. Go to your repository on GitHub
2. Click "Watch" at the top right
3. Select "All Activity" or customize to include "Actions"

## What Notifications You'll Receive

### By Default (No Configuration Needed)

GitHub will automatically email you when:
- ✅ A workflow run **fails**
- ✅ A workflow job **fails**
- ✅ A workflow is **cancelled**

### Optional: Success Notifications

You can also enable success notifications through GitHub's native system:

1. Go to: https://github.com/settings/notifications
2. Scroll to "Actions" section
3. Configure notifications for successful workflow runs

**Note:** Success notifications are **not enabled by default** - you must explicitly enable them in your GitHub notification settings. This is a native GitHub feature and doesn't require any third-party integrations.

### What Each Email Includes

- Workflow name and status
- Direct link to the workflow run
- Timestamp and triggering event
- Branch/commit information

## Cost

**100% FREE** - This is part of GitHub's core functionality, not a paid feature.

## Comparison: Native vs Custom Email Notifications

### GitHub Native Notifications (Free, No Setup)
- ✅ Alerts on workflow failures (default)
- ✅ Can enable alerts on workflow success (optional, in settings)
- ✅ Zero configuration required
- ✅ Free forever
- ✅ Reliable (GitHub infrastructure)
- ❌ Cannot customize message content
- ❌ **Cannot alert on custom conditions (like pressure drops)**
- ❌ **Only reports workflow status, not what happened inside the workflow**

**Example notification:** "Workflow run succeeded" (even if pressure drop was detected)

### Custom Email via Gmail (Requires Setup)
- ✅ **Can alert on custom conditions (pressure drops)**
- ✅ **Sends detailed alerts about what was detected**
- ✅ Fully customizable email content
- ✅ Can choose exact recipient
- ❌ Requires Gmail app-specific password setup
- ❌ Requires adding GitHub secrets
- ❌ Depends on third-party email service

**Example notification:** "⚠️ Barometric Pressure Drop Detected - Current: 1010 hPa, Previous: 1013 hPa"

## Recommendation

**For workflow monitoring only:** Use GitHub's native notifications (no setup required)
- You'll know if the workflow fails to run
- You'll know if the workflow succeeds (if you enable success notifications)
- You won't know about pressure drops detected within successful workflows

**For pressure drop alerts:** You must use custom email alerts (Option 2 in NOTIFICATIONS.md)
- Native notifications can't report custom conditions like pressure drops
- Custom Gmail alerts send separate emails when pressure drops are detected
- These work independently from the workflow success/failure status

## Frequently Asked Questions

### Q: Do I need to set up Gmail to receive workflow failure notifications?
**A:** No! GitHub sends these automatically to your GitHub notification email.

### Q: Where do these emails come from?
**A:** They come from `notifications@github.com` and look like standard GitHub notification emails.

### Q: Can I customize the email content?
**A:** No, GitHub's native notifications have a standard format. For custom content, you'd need to set up custom email alerts (Option 2 in NOTIFICATIONS.md).

### Q: Will I receive too many emails?
**A:** By default, you only receive emails for workflow failures. Success notifications are opt-in - you can enable them in your GitHub notification settings at https://github.com/settings/notifications if you want to be notified of successful runs too.

### Q: Does this work for scheduled workflows?
**A:** Yes! GitHub sends notifications for scheduled workflow failures just like manually triggered ones.

### Q: Can I get success notifications without third-party integrations?
**A:** Yes! GitHub's native notification system supports success notifications. Go to https://github.com/settings/notifications and configure the Actions section to include successful workflow runs. This is a built-in GitHub feature - no third-party services needed.

### Q: Will GitHub's native success notification tell me about pressure drops?
**A:** No. GitHub's native notifications only report **workflow-level status** (success/failure/cancelled). They don't know about custom conditions like pressure drops that occur within the workflow. Even if a pressure drop is detected, the workflow completes successfully, so you'd just get a generic "workflow succeeded" email with no mention of the pressure drop.

### Q: What if I want notifications for pressure drops, not just failures?
**A:** You'll need to set up custom email alerts using Gmail (see SETUP_NOTIFICATIONS.md). The native notifications only cover workflow status (success/failure/cancelled), not custom conditions within the workflow. The custom Gmail integration sends a separate email specifically when pressure drops are detected, with details about the drop.

## Testing Native Notifications

1. Ensure you're watching the repository
2. Go to Actions tab
3. Manually trigger the workflow with "Run workflow"
4. If it fails, you'll receive an email at your GitHub notification address
5. Check your spam folder if you don't see it

## Further Reading

- [NOTIFICATIONS.md](NOTIFICATIONS.md) - All notification options
- [SETUP_NOTIFICATIONS.md](SETUP_NOTIFICATIONS.md) - Setting up custom Gmail alerts
- [GitHub Notifications Documentation](https://docs.github.com/en/account-and-settings/managing-subscriptions-and-notifications-on-github)
