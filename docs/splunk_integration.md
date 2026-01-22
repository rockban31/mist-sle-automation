# Splunk Integration Guide

## Overview

The Mist SLE automation pipeline sends comprehensive audit events to Splunk HTTP Event Collector (HEC) for monitoring, analytics, and compliance.

---

## HEC Configuration

### Setup Splunk HEC

1. **Enable HEC**:
   ```
   Settings → Data Inputs → HTTP Event Collector → Global Settings
   ✓ Enable SSL
   ✓ Enable HEC
   ```

2. **Create HEC Token**:
   ```
   Settings → Data Inputs → HTTP Event Collector → New Token
   Name: mist-sle-automation
   Source Type: _json
   Index: mist_automation
   ```

3. **Note Configuration**:
   - HEC Endpoint: `https://splunk.example.com:8088/services/collector`
   - Token: Save for GitHub Secrets

### GitHub Secrets

Add to repository:
```
SPLUNK_HEC_ENDPOINT=https://splunk.example.com:8088/services/collector
SPLUNK_HEC_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## Event Types

### 1. SLE Detection

**Sourcetype**: `mist:sle:detection`

**Payload**:
```json
{
  "time": 1706022000,
  "host": "github-actions",
  "source": "mist_automation",
  "sourcetype": "mist:sle:detection",
  "event": {
    "event_type": "sle_detection",
    "ap_id": "AABBCC",
    "sle": "throughput",
    "severity": "high",
    "source": "splunk",
    "timestamp": "2026-01-22T15:00:00Z"
  }
}
```

---

### 2. Diagnostics

**Sourcetype**: `mist:sle:diagnostics`

**Payload**:
```json
{
  "event": {
    "event_type": "diagnostics",
    "ap_id": "AABBCC",
    "diagnostics": {
      "client_count": 15,
      "ap_stats": {...},
      "sle_diagnostics": {...}
    },
    "timestamp": "2026-01-22T15:01:00Z"
  }
}
```

---

### 3. Remediation

**Sourcetype**: `mist:sle:remediation`

**Payload**:
```json
{
  "event": {
    "event_type": "remediation",
    "ap_id": "AABBCC",
    "action": "reboot",
    "result": {
      "status": "success",
      "message": "Reboot command issued successfully"
    },
    "timestamp": "2026-01-22T15:02:00Z"
  }
}
```

---

### 4. Validation

**Sourcetype**: `mist:sle:validation`

**Payload**:
```json
{
  "event": {
    "event_type": "validation",
    "ap_id": "AABBCC",
    "sle": "throughput",
    "result": {
      "status": "restored",
      "final_score": 95.2,
      "duration": 180
    },
    "timestamp": "2026-01-22T15:05:00Z"
  }
}
```

---

### 5. Ticket Actions

**Sourcetype**: `mist:sle:ticketing`

**Payload**:
```json
{
  "event": {
    "event_type": "ticket_action",
    "ticket_id": "334289",
    "action": "create",
    "ap_id": "AABBCC",
    "sle": "throughput",
    "timestamp": "2026-01-22T15:00:30Z"
  }
}
```

---

### 6. Workflow Complete

**Sourcetype**: `mist:sle:workflow`

**Payload**:
```json
{
  "event": {
    "event_type": "workflow_complete",
    "ap_id": "AABBCC",
    "sle": "throughput",
    "status": "success",
    "metrics": {
      "mttr": 300,
      "automation_success": true
    },
    "timestamp": "2026-01-22T15:05:00Z"
  }
}
```

---

## Splunk Queries

### All Automation Events

```spl
index=mist_automation sourcetype=mist:sle:*
```

### Automation Success Rate

```spl
index=mist_automation sourcetype=mist:sle:workflow
| stats count by status
| eval success_rate=round((success/(success+failed))*100, 2)
```

### MTTR (Mean Time to Remediate)

```spl
index=mist_automation sourcetype=mist:sle:workflow status=success
| stats avg(metrics.mttr) as avg_mttr, median(metrics.mttr) as median_mttr
| eval avg_mttr_min=round(avg_mttr/60, 2)
| eval median_mttr_min=round(median_mttr/60, 2)
```

### Top AP Offenders

```spl
index=mist_automation sourcetype=mist:sle:detection
| stats count by ap_id
| sort -count
| head 10
```

### Remediation Actions by Type

```spl
index=mist_automation sourcetype=mist:sle:remediation
| stats count by action, result.status
```

### Guardrail Blocks

```spl
index=mist_automation sourcetype=mist:sle:remediation result.status=blocked
| stats count by result.reason
```

---

## Dashboard Panels

### 1. SLE Automation Overview

```xml
<panel>
  <title>SLE Automation Overview</title>
  <single>
    <search>
      <query>index=mist_automation sourcetype=mist:sle:workflow
      | stats count as total_workflows</query>
    </search>
  </single>
</panel>
```

### 2. MTTR Trend

```xml
<panel>
  <title>MTTR Trend (Last 7 Days)</title>
  <chart>
    <search>
      <query>index=mist_automation sourcetype=mist:sle:workflow status=success
      | timechart span=1d avg(metrics.mttr) as avg_mttr
      | eval avg_mttr_min=round(avg_mttr/60, 2)</query>
    </search>
    <option name="charting.chart">line</option>
  </chart>
</panel>
```

### 3. Success Rate by SLE Type

```xml
<panel>
  <title>Success Rate by SLE Type</title>
  <chart>
    <search>
      <query>index=mist_automation sourcetype=mist:sle:workflow
      | stats count by sle, status
      | chart count over sle by status</query>
    </search>
    <option name="charting.chart">column</option>
  </chart>
</panel>
```

---

## Alerting

### Failed Remediation

```spl
index=mist_automation sourcetype=mist:sle:workflow status=failed
| eval alert_message="SLE automation failed for AP " . ap_id . " - SLE: " . sle
```

**Alert Conditions**:
- Trigger: Search returns results
- Throttle: 30 minutes
- Action: Email ops team

---

### High MTTR

```spl
index=mist_automation sourcetype=mist:sle:workflow status=success
| stats avg(metrics.mttr) as avg_mttr
| where avg_mttr > 600
```

**Alert Conditions**:
- Trigger: Avg MTTR > 10 minutes
- Schedule: Every hour
- Action: Notify automation team

---

### Repeated AP Failures

```spl
index=mist_automation sourcetype=mist:sle:detection
| stats count by ap_id
| where count > 5
```

**Alert Conditions**:
- Trigger: Same AP > 5 failures in 24 hours
- Schedule: Every 4 hours
- Action: Create RCA ticket

---

## Data Model

### Field Extraction

```conf
[mist:sle:*]
INDEXED_EXTRACTIONS = json
KV_MODE = json
TIME_PREFIX = "timestamp"\s*:\s*"
TIME_FORMAT = %Y-%m-%dT%H:%M:%SZ
```

### Field Aliases

```conf
[mist:sle:*]
FIELDALIAS-ap = event.ap_id AS ap_id
FIELDALIAS-sle = event.sle AS sle_type
FIELDALIAS-severity = event.severity AS severity
FIELDALIAS-status = event.status AS workflow_status
```

---

## Retention & Archival

Recommended index settings:

```conf
[mist_automation]
coldPath = $SPLUNK_DB/mist_automation/colddb
homePath = $SPLUNK_DB/mist_automation/db
thawedPath = $SPLUNK_DB/mist_automation/thaweddb
maxHotBuckets = 3
maxDataSize = auto
frozenTimePeriodInSecs = 7776000  # 90 days
```

---

## Testing

### Send Test Event

```bash
python src/splunk.py \
  --ap_id TEST123 \
  --sle throughput \
  --status success
```

### Verify in Splunk

```spl
index=mist_automation ap_id=TEST123 | head 1
```

---

## Troubleshooting

### Events Not Appearing

**Check**:
1. HEC endpoint reachable
2. Token valid
3. Index exists
4. Time parsing correct

**Test**:
```bash
curl -k https://splunk.example.com:8088/services/collector \
  -H "Authorization: Splunk YOUR_TOKEN" \
  -d '{"event": "test"}'
```

---

### SSL Certificate Errors

**Solution**: Use `-k` flag for self-signed certs (testing only)

**Production**: Import CA cert or disable SSL verification (not recommended)

---

## Performance

### Event Volume

Estimated events per workflow:
- Detection: 1
- Diagnostics: 1
- Remediation: 1
- Validation: 1
- Ticket actions: 3 (create, update, close)
- Workflow complete: 1

**Total**: ~8 events per workflow

**Daily estimate** (100 workflows): 800 events/day ≈ 0.8 GB/year (as JSON)

---

## References

- [Splunk HEC Documentation](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector)
- [Splunk Search Reference](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference)
- [Splunk Dashboards](https://docs.splunk.com/Documentation/Splunk/latest/Viz/Dashboards)

---

**For questions, contact the automation or Splunk admin team**
