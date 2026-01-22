# Zendesk Integration Guide

## Overview

This document describes how the Mist SLE automation pipeline integrates with Zendesk for incident ticketing and tracking.

---

## API Configuration

### Authentication

The integration uses **API Token authentication**:

```python
auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)
```

### Required Secrets

| Secret | Format | Example |
|--------|--------|---------|
| `ZENDESK_SUBDOMAIN` | Your subdomain only | `acme` (for acme.zendesk.com) |
| `ZENDESK_EMAIL` | Email address | `automation@acme.com` |
| `ZENDESK_API_TOKEN` | API token | `aBcD1234...` |
| `ZENDESK_GROUP_ID` | Group ID (optional) | `123456789` |

---

## Ticket Lifecycle

### 1. Ticket Creation

**Trigger**: SLE failure detected

**API Call**:
```
POST /api/v2/tickets.json
```

**Payload**:
```json
{
  "ticket": {
    "subject": "Mist SLE Failure: throughput on AP AABBCC",
    "comment": {
      "body": "**Automated SLE Detection Alert**\n\n- **Access Point**: AABBCC\n- **SLE Metric**: throughput\n- **Severity**: high\n- **Detection Time**: 2026-01-22T15:00:00Z\n- **Source**: Splunk → GitHub Actions → Automation Pipeline\n\nAutomated remediation workflow has been initiated."
    },
    "priority": "high",
    "type": "incident",
    "tags": ["mist", "wireless", "sle", "automation", "throughput", "AABBCC"]
  }
}
```

**Response**:
```json
{
  "ticket": {
    "id": 334289,
    "status": "new",
    "priority": "high",
    ...
  }
}
```

---

### 2. Ticket Updates

**Trigger**: Workflow progress (diagnostics, remediation, validation)

**API Call**:
```
PUT /api/v2/tickets/{ticket_id}.json
```

**Example Updates**:

**After Diagnostics**:
```json
{
  "ticket": {
    "comment": {
      "body": "Diagnostics completed. AP analysis in progress. Client count: 15"
    }
  }
}
```

**After Remediation**:
```json
{
  "ticket": {
    "comment": {
      "body": "Remediation executed: AP reboot initiated. Waiting for stabilization and SLE validation."
    },
    "status": "pending"
  }
}
```

**Remediation Blocked**:
```json
{
  "ticket": {
    "comment": {
      "body": "Remediation blocked by guardrails: Client count (2) below minimum threshold (3). Manual investigation required."
    }
  }
}
```

---

### 3. Ticket Closure

**Trigger**: Successful SLE restoration

**API Call**:
```
PUT /api/v2/tickets/{ticket_id}.json
```

**Payload**:
```json
{
  "ticket": {
    "status": "solved",
    "comment": {
      "body": "**Automated Resolution**\n\nSLE metrics successfully restored. Final score: 95.2\n\n- **Resolution Time**: 2026-01-22T15:08:30Z\n- **Status**: SLE restored to acceptable levels\n- **MTTR**: Reduced via automation\n\nThis ticket has been automatically resolved by the Mist SLE automation pipeline."
    }
  }
}
```

---

## Priority Mapping

The pipeline maps SLE severity to Zendesk priority:

| SLE Severity | Zendesk Priority | Use Case |
|--------------|------------------|----------|
| `critical` | `urgent` | DHCP/DNS/Gateway failures, >1 AP simultaneously |
| `high` | `high` | High retries, throughput failures |
| `medium` | `normal` | Medium-level SLE degradation |
| `low` | `low` | Minor SLE issues |

**Configured in `src/zendesk.py`**:
```python
SLE_PRIORITY_MAP = {
    "critical": "urgent",
    "high": "high",
    "medium": "normal",
    "low": "normal"
}
```

---

## Ticket Fields

### Standard Fields

All automated tickets include:

- **Subject**: `Mist SLE Failure: {sle} on AP {ap_id}`
- **Type**: `incident`
- **Priority**: Based on severity
- **Status**: `new` → `pending` → `solved`

### Tags

All tickets are tagged with:
- `mist`
- `wireless`
- `sle`
- `automation`
- `{sle_type}` (e.g., `throughput`)
- `{ap_id}` (e.g., `AABBCC`)

**Benefits**:
- Easy filtering and reporting
- Identify automation-generated tickets
- Track specific AP or SLE issues

---

## Group Assignment

If `ZENDESK_GROUP_ID` is configured, tickets are automatically assigned to the specified group:

```json
{
  "ticket": {
    ...
    "group_id": 123456789
  }
}
```

**How to find your Group ID**:
1. Go to Zendesk Admin → Groups
2. Click on the desired group
3. Note the ID in the URL: `https://yourcompany.zendesk.com/admin/groups/{GROUP_ID}`

---

## Error Handling

### API Failures

The integration handles failures gracefully:

```python
try:
    response = requests.post(url, auth=auth, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error(f"Failed to create Zendesk ticket: {e}")
    raise
```

**Workflow Behavior**:
- If Zendesk API fails, the workflow continues
- Errors are logged to GitHub Actions output
- Splunk audit still captures the event

---

## Monitoring & Metrics

### SLA Tracking

Zendesk's built-in SLA features can track:
- **First Reply Time**: Time to first comment (should be near-instant for automation)
- **Full Resolution Time**: MTTR for automated remediation

### Dashboards

Recommended Zendesk reports:
1. **Tickets by Tag**: Filter `automation` tag
2. **Resolution Time**: Compare automated vs. manual
3. **Automation Success Rate**: `solved` vs. escalated tickets

### Macros

Create Zendesk macros for common actions:
- **Escalate to Ops**: For failed automations
- **Request RCA**: For repeat offenders
- **Add to Maintenance Window**: To pause automation

---

## Best Practices

### 1. Ticket Deduplication

**Problem**: Multiple workflows creating duplicate tickets

**Solution**: Pass existing `zendesk_ticket` ID to workflow:
```yaml
zendesk_ticket: '334289'
```

### 2. Business Hours

Configure in `rules/sle_rules.yaml`:
```yaml
guardrails:
  business_hours_only: true
  business_hours:
    start: "08:00"
    end: "18:00"
    timezone: "UTC"
```

### 3. Notification Rules

Configure Zendesk triggers to:
- Email on ticket creation (optional - may be noisy)
- Notify on escalation (validation failures)
- Alert on repeat AP issues

### 4. Ticket Archival

Set retention policies:
- Auto-close tickets after 7 days of inactivity
- Archive solved tickets after 30 days
- Retain analytics data indefinitely

---

## Testing

### Manual Ticket Creation

```bash
python src/zendesk.py \
  --ap_id TEST123 \
  --sle throughput \
  --severity high \
  --action create
```

### Update Ticket

```bash
python src/zendesk.py \
  --ticket 334289 \
  --action update \
  --comment "Test update from automation"
```

### Close Ticket

```bash
python src/zendesk.py \
  --ticket 334289 \
  --action close \
  --comment "Test closure"
```

---

## Troubleshooting

### Issue: "Couldn't authenticate you"

**Cause**: Invalid credentials

**Check**:
1. Email format: `user@domain.com/token`
2. API token is active (not expired)
3. User has agent permissions

**Test**:
```bash
curl -u "user@domain.com/token:YOUR_API_TOKEN" \
  https://yourcompany.zendesk.com/api/v2/users/me.json
```

---

### Issue: "RecordNotFound"

**Cause**: Invalid ticket ID

**Check**:
1. Ticket ID exists
2. User has access to ticket
3. Ticket not deleted

---

### Issue: Tickets not auto-closing

**Cause**: Validation not completing successfully

**Debug**:
1. Check `validation.json` artifact
2. Review SLE validation logs
3. Verify threshold configuration

---

## API Rate Limits

Zendesk enforces rate limits:
- **Standard**: 700 requests/minute
- **Burst**: Up to 1400 requests in 1 minute

**Our usage**: Low (~5 requests per workflow)

**Recommendation**: No special handling needed

---

## Security

### API Token Permissions

Use a dedicated automation account with:
- **Agent role** (minimum required)
- **Limited to specific groups** (optional)
- **No admin permissions**

### Token Rotation

Rotate tokens every 90 days:
1. Generate new token in Zendesk Admin
2. Update GitHub Secret
3. Deprecate old token after 24 hours

---

## Future Enhancements

- [ ] Add custom fields (AP ID, SLE type, site)
- [ ] Implement ticket linking for related issues
- [ ] Add SLA breach alerts
- [ ] Integration with Zendesk Guide for KB articles
- [ ] Automated ticket templates

---

## References

- [Zendesk API Documentation](https://developer.zendesk.com/api-reference/)
- [Tickets API](https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/)
- [Authentication](https://developer.zendesk.com/api-reference/introduction/security-and-auth/)

---

**For questions or issues, contact the automation team**
