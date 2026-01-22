# Mist SLE Proactive Automation Pipeline

[![Mist SLE Automation](https://img.shields.io/badge/Mist-SLE%20Automation-blue)](https://www.mist.com/)
[![Zendesk Integration](https://img.shields.io/badge/Zendesk-Integrated-green)](https://www.zendesk.com/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF)](https://github.com/features/actions)

## 🎯 Overview

Production-ready **closed-loop SLE automation pipeline** that integrates Mist Cloud, Splunk, GitHub Actions, and Zendesk to automatically detect, diagnose, remediate, and validate wireless network Service Level Expectation (SLE) failures.

### Key Features

✅ **Automated SLE Detection** - Webhook-driven alerts from Mist via Splunk  
✅ **Intelligent Diagnostics** - Comprehensive AP health and SLE metrics analysis  
✅ **Safe Remediation** - Guardrail-protected AP reboot with client count checks  
✅ **Validation Loop** - Automated SLE polling to confirm restoration  
✅ **Zendesk Ticketing** - Auto-create, update, and close incidents  
✅ **Splunk Audit Trail** - Complete workflow observability and MTTR metrics  

---

## 🏗 Architecture

```
Mist Cloud
   │ Webhook → Splunk (HEC)
   ↓
Splunk → Workflow Dispatch → GitHub Actions
   ↓
GitHub Actions:
   ├─ Diagnostics (Mist APIs)
   ├─ Decision Logic
   ├─ Remediation (Mist APIs)
   ├─ Validation (SLE polling)
   └─ Audit → Splunk
   ↓
Zendesk:
   ├─ Ticket Create
   ├─ Ticket Update
   └─ Ticket Auto-Closure
```

---

## 📁 Project Structure

```
mist-proactive-automation/
├─ .github/
│  └─ workflows/
│     └─ sle_automation.yml      # Main GitHub Actions workflow
├─ src/
│  ├─ mist.py                    # Mist API client
│  ├─ diagnostics.py             # AP diagnostics module
│  ├─ remediation.py             # Remediation actions
│  ├─ validation.py              # SLE validation
│  ├─ zendesk.py                 # Zendesk ticketing
│  └─ splunk.py                  # Splunk audit
├─ rules/
│  └─ sle_rules.yaml             # SLE thresholds & remediation rules
├─ tests/                        # Unit tests (to be added)
├─ docs/                         # Documentation
├─ requirements.txt              # Python dependencies
└─ README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites

- GitHub repository with Actions enabled
- Mist Cloud account with API token
- Zendesk account with API access
- Splunk instance with HEC endpoint (optional but recommended)

### Step 1: Configure Secrets

Add the following secrets to your GitHub repository:

| Secret | Description | Required |
|--------|-------------|----------|
| `MIST_API_TOKEN` | Mist Cloud API token | ✅ Yes |
| `SITE_ID` | Mist site ID | ✅ Yes |
| `ZENDESK_SUBDOMAIN` | Zendesk subdomain (e.g., `yourcompany`) | ✅ Yes |
| `ZENDESK_EMAIL` | Zendesk user email | ✅ Yes |
| `ZENDESK_API_TOKEN` | Zendesk API token | ✅ Yes |
| `ZENDESK_GROUP_ID` | Zendesk group ID for assignment | ⚠️ Optional |
| `SPLUNK_HEC_ENDPOINT` | Splunk HEC URL | ⚠️ Optional |
| `SPLUNK_HEC_TOKEN` | Splunk HEC token | ⚠️ Optional |

**To add secrets:**
```
Repository → Settings → Secrets and variables → Actions → New repository secret
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Test Workflow Manually

Trigger the workflow manually from GitHub Actions:

```
Actions → Mist SLE Proactive Automation → Run workflow
```

Provide:
- **AP ID**: Access Point ID (e.g., `00000000-0000-0000-0000-5c5b35ae1fe0`)
- **SLE**: Metric type (e.g., `throughput`, `successful-connects`)
- **Severity**: `critical`, `high`, `medium`, or `low`

---

## 🔧 Configuration

### SLE Rules (`rules/sle_rules.yaml`)

Configure:
- **SLE Thresholds**: Score thresholds for severity levels
- **Remediation Strategies**: Actions per SLE type
- **Guardrails**: Safety limits (min clients, reboot intervals)
- **Validation**: Polling intervals and success criteria

Example:
```yaml
guardrails:
  min_clients: 3
  min_reboot_interval: 1800
  max_daily_reboots: 3
```

### Zendesk Priority Mapping

The pipeline automatically maps SLE severity to Zendesk priority:

| SLE Severity | Zendesk Priority |
|--------------|------------------|
| critical | urgent |
| high | high |
| medium | normal |
| low | low |

---

## 📊 Workflow Stages

### Stage 1: Detection
- Mist webhook → Splunk alert
- Splunk triggers GitHub Actions workflow

### Stage 2: Ticket Creation
- Create Zendesk incident
- Tag with AP ID, SLE type, automation markers

### Stage 3: Diagnostics
- Fetch AP stats, details, client count
- Retrieve current SLE metrics
- Generate diagnostic report

### Stage 4: Remediation
- **Guardrail checks**:
  - Client count ≥ 3
  - Last reboot ≥ 30 minutes ago
- Execute AP reboot if checks pass

### Stage 5: Validation
- Wait 60s for stabilization
- Poll SLE metrics every 60s (max 5 attempts)
- Success: SLE score ≥ 90

### Stage 6: Ticket Update
- Update Zendesk with remediation progress
- Include validation results

### Stage 7: Auto-Closure
- **Success**: Close ticket, mark as resolved
- **Failure**: Escalate to ops team, keep ticket open

---

## 🛡️ Guardrails

The system implements multiple safety guardrails:

✅ **Client Count Check**: Only remediate if ≥3 clients connected  
✅ **Reboot Interval**: Prevent frequent reboots (min 30 min)  
✅ **Daily Limits**: Maximum 3 reboots per AP per day  
✅ **Validation Loop**: Confirm SLE restoration before closure  
✅ **Error Handling**: Graceful failure with manual escalation  

---

## 📈 Monitoring & Metrics

### Splunk Dashboards

Track key metrics:
- **MTTA** (Mean Time to Acknowledge)
- **MTTR** (Mean Time to Remediate)
- **Automation Success Rate**
- **Top AP Offenders**
- **Ticket Volume by SLE Type**

### GitHub Actions Artifacts

Each workflow run saves:
- `diagnostics.json` - AP health snapshot
- `remediation.json` - Remediation actions taken
- `validation.json` - SLE validation results
- Retention: 30 days

---

## 🧪 Testing

### Manual Testing

```bash
# Test Mist API connection
python src/mist.py

# Test diagnostics
python src/diagnostics.py --ap_id <AP_ID> --sle throughput

# Test remediation (dry-run)
python src/remediation.py --ap_id <AP_ID> --sle throughput

# Test validation
python src/validation.py --ap_id <AP_ID> --sle throughput
```

### Unit Tests

```bash
# Run unit tests (to be implemented)
pytest tests/
```

---

## 🔐 Security Best Practices

1. **Never commit secrets** - Use GitHub Secrets only
2. **Rotate API tokens** regularly
3. **Audit trail** - All actions logged to Splunk
4. **Least privilege** - Use read-only tokens where possible
5. **Network policies** - Restrict GitHub Actions runner IPs

---

## 🚨 Troubleshooting

### Common Issues

**Issue**: Workflow fails with "MIST_API_TOKEN not set"  
**Solution**: Verify secrets are configured in GitHub repository settings

**Issue**: Remediation blocked by guardrails  
**Solution**: Check AP client count and uptime in diagnostics output

**Issue**: Validation timeout  
**Solution**: Increase `max_attempts` or `poll_interval` in `rules/sle_rules.yaml`

**Issue**: Zendesk ticket not created  
**Solution**: Verify Zendesk credentials and subdomain

### Debug Mode

Enable verbose logging:
```bash
export LOG_LEVEL=DEBUG
python src/diagnostics.py --ap_id <AP_ID> --sle throughput
```

---

## 🛣️ Roadmap

- [ ] Multi-AP correlation (detect site-wide issues)
- [ ] WLAN reset remediation
- [ ] RRM (Radio Resource Management) adjustments
- [ ] Machine learning for remediation selection
- [ ] ServiceNow integration option
- [ ] Slack notifications
- [ ] Self-healing configuration drift detection

---

## 📚 Additional Documentation

- [Mist API Documentation](https://api.mist.com/)
- [Zendesk API Reference](https://developer.zendesk.com/api-reference/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Splunk HEC Documentation](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 💬 Support

For issues or questions:
- Open a GitHub issue
- Contact the network automation team

---

**Built with ❤️ for proactive network operations**
