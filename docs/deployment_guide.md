# Deployment Guide

## Overview

This guide walks you through deploying the Mist SLE automation pipeline to production.

---

## Prerequisites

- [ ] GitHub account with repository admin access
- [ ] Mist Cloud account with API token
- [ ] Zendesk account with API access
- [ ] Splunk instance with HEC endpoint (optional)
- [ ] Basic understanding of GitHub Actions

---

## Step-by-Step Deployment

### Step 1: Fork or Clone Repository

**Option A: Fork Repository**
```bash
# Fork via GitHub UI, then clone
git clone https://github.com/YOUR_USERNAME/mist-sle-automation.git
cd mist-sle-automation
```

**Option B: Create New Repository**
```bash
# Create repository in GitHub UI, then
git init
git remote add origin https://github.com/YOUR_ORG/mist-sle-automation.git
```

---

### Step 2: Obtain API Credentials

#### Mist API Token

1. Log in to Mist Cloud: https://manage.mist.com/
2. Navigate to **Organization → Settings → API Tokens**
3. Click **Create Token**
4. Set privileges: **Read/Write**
5. Copy token and site ID

#### Zendesk API Token

1. Log in to Zendesk Admin: https://yourcompany.zendesk.com/admin/
2. Navigate to **Apps and Integrations → APIs → Zendesk API**
3. Enable **Token Access**
4. Click **Add API Token**
5. Enter description: "Mist SLE Automation"
6. Copy token

#### Splunk HEC Token (Optional)

1. Log in to Splunk
2. **Settings → Data Inputs → HTTP Event Collector**
3. Enable HEC if not already enabled
4. Click **New Token**
5. Configure:
   - Name: mist-sle-automation
   - Source Type: `_json`
   - Index: `mist_automation` (create if needed)
6. Copy token and HEC endpoint

---

### Step 3: Configure GitHub Secrets

1. Go to repository **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add the following secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `MIST_API_TOKEN` | Your Mist API token | `abc123...` |
| `SITE_ID` | Your Mist site ID | `12345678-1234-...` |
| `ZENDESK_SUBDOMAIN` | Zendesk subdomain only | `acme` |
| `ZENDESK_EMAIL` | Automation account email | `automation@acme.com` |
| `ZENDESK_API_TOKEN` | Zendesk API token | `xyz789...` |
| `ZENDESK_GROUP_ID` | (Optional) Group ID | `123456789` |
| `SPLUNK_HEC_ENDPOINT` | (Optional) HEC URL | `https://splunk.acme.com:8088/services/collector` |
| `SPLUNK_HEC_TOKEN` | (Optional) HEC token | `def456...` |

**Screenshot Guide**:
```
Settings → Secrets and variables → Actions → New repository secret
Name: MIST_API_TOKEN
Secret: [paste token]
[Add secret]
```

---

### Step 4: Verify Workflow Files

Ensure `.github/workflows/sle_automation.yml` exists:

```bash
ls -la .github/workflows/sle_automation.yml
```

If missing, copy from this repository.

---

### Step 5: Test Workflow Manually

1. Go to GitHub repository
2. Click **Actions** tab
3. Select **Mist SLE Proactive Automation** workflow
4. Click **Run workflow** (top right)
5. Fill in test parameters:
   - **AP ID**: Test AP ID from Mist (e.g., `00000000-0000-0000-0000-5c5b35ae1fe0`)
   - **SLE**: `throughput`
   - **Severity**: `high`
6. Click **Run workflow**

**Expected Result**:
- Workflow starts and completes successfully
- Zendesk ticket created
- Diagnostics, remediation, validation execute
- Ticket updated and potentially closed

---

### Step 6: Configure Splunk Alert (Optional)

If using Splunk for triggering:

**Create Saved Search**:
```spl
index=mist sourcetype=mist:webhook
| where sle_score < 70
| eval ap_id=device_id
| eval sle=sle_type
| eval severity=case(
    sle_score < 60, "critical",
    sle_score < 70, "high",
    sle_score < 80, "medium",
    1=1, "low"
  )
| table ap_id, sle, severity
```

**Trigger Action**: Webhook to GitHub Actions

**Webhook URL**:
```
https://api.github.com/repos/YOUR_ORG/REPO/actions/workflows/sle_automation.yml/dispatches
```

**Headers**:
```
Authorization: Bearer YOUR_GITHUB_TOKEN
Content-Type: application/json
```

**Body**:
```json
{
  "ref": "main",
  "inputs": {
    "ap_id": "$result.ap_id$",
    "sle": "$result.sle$",
    "severity": "$result.severity$"
  }
}
```

---

### Step 7: Set Up Monitoring

#### GitHub Actions Monitoring

1. Enable email notifications:
   - **Settings → Notifications → Actions**
   - Check "Send notifications for failed workflows"

2. Review workflow runs regularly:
   - **Actions** tab shows all runs
   - Download artifacts for debugging

#### Splunk Dashboard

Import dashboard from `docs/splunk_dashboard.xml` (if provided) or build custom dashboard with queries from `docs/splunk_integration.md`.

#### Zendesk Reporting

Create Zendesk report:
1. **Admin → Reports → Add Report**
2. Filter by tag: `automation`
3. Visualize:
   - Tickets created over time
   - Average resolution time
   - Success vs. escalation rate

---

### Step 8: Production Tuning

#### Guardrails

Edit `rules/sle_rules.yaml`:

```yaml
guardrails:
  min_clients: 5  # Increase for production
  min_reboot_interval: 3600  # 1 hour
  max_daily_reboots: 2  # Conservative limit
  business_hours_only: true  # Enable if desired
```

#### Validation

Adjust validation thresholds:

```yaml
validation:
  poll_interval: 120  # Longer interval
  max_attempts: 10  # More attempts
  threshold_score: 92  # Higher bar
```

---

### Step 9: Enable Business Hours (Optional)

If restricting to business hours:

```yaml
guardrails:
  business_hours_only: true
  business_hours:
    start: "08:00"
    end: "18:00"
    timezone: "America/New_York"
```

**Note**: Implement business hours logic in `src/remediation.py` (currently placeholder).

---

### Step 10: Create Runbook

Document your operational procedures:

**Runbook Template**:
```markdown
# Mist SLE Automation Runbook

## Normal Operation
- Workflow triggered by Splunk alert
- Ticket created in Zendesk
- Remediation auto-executes if guardrails pass
- Ticket auto-closes on success

## Manual Intervention
- If validation fails, ticket escalated to ops
- Review diagnostics artifact in GitHub Actions
- Investigate AP manually in Mist dashboard

## Emergency Stop
- Disable workflow: Repository Settings → Actions → Disable workflow
- Close open tickets manually

## Escalation
- Contact: network-ops@company.com
- Slack: #network-automation
```

---

## Deployment Checklist

- [ ] Repository created and configured
- [ ] All GitHub Secrets added
- [ ] Workflow file deployed
- [ ] Test run completed successfully
- [ ] Splunk integration tested (if applicable)
- [ ] Zendesk ticket workflow verified
- [ ] Monitoring alerts configured
- [ ] Guardrails tuned for production
- [ ] Team trained on runbook
- [ ] Emergency contacts documented

---

## Rollback Plan

If issues occur:

1. **Immediate**: Disable workflow in GitHub Actions
2. **Short-term**: Revert to previous commit
3. **Long-term**: Review logs, fix issues, redeploy

**Disable Workflow**:
```
Repository → Settings → Actions → [Workflow] → Disable workflow
```

---

## Maintenance

### Weekly
- [ ] Review failed workflows
- [ ] Check Zendesk escalations
- [ ] Validate MTTR metrics in Splunk

### Monthly
- [ ] Review guardrail settings
- [ ] Analyze top offending APs
- [ ] Tune SLE thresholds if needed

### Quarterly
- [ ] Rotate API tokens
- [ ] Update dependencies
- [ ] Review and improve runbook

---

## Troubleshooting

See individual integration docs:
- `docs/zendesk_integration.md`
- `docs/splunk_integration.md`
- `README.md`

---

## Support

- **GitHub Issues**: Open an issue for bugs or feature requests
- **Email**: network-automation@company.com
- **Slack**: #mist-automation

---

**Deployment completed! 🚀**
