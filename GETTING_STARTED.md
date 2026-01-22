# 🚀 GETTING STARTED

Welcome to the **Mist SLE Proactive Automation Pipeline**! This guide will get you up and running quickly.

---

## 📋 Prerequisites

Before you begin, ensure you have:

- [x] **Python 3.11+** installed
- [x] **GitHub account** with repository access
- [x] **Mist Cloud account** with API access
- [x] **Zendesk account** with API token
- [x] (Optional) **Splunk instance** with HEC endpoint

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Clone the Repository

```bash
cd "d:\coding related\incident _auto_ resolve_mist"
```

### Step 2: Run Quick Start Script

```powershell
# Windows
.\quickstart.ps1

# This script will:
# ✅ Check Python installation
# ✅ Create virtual environment
# ✅ Install dependencies
# ✅ Create .env template
# ✅ Run tests
```

### Step 3: Configure Environment

Edit `.env` file with your credentials:

```bash
# Mist API Configuration
MIST_API_TOKEN=your_token_here
SITE_ID=your_site_id_here

# Zendesk Configuration
ZENDESK_SUBDOMAIN=yourcompany
ZENDESK_EMAIL=automation@yourcompany.com
ZENDESK_API_TOKEN=your_token_here

# Splunk Configuration (Optional)
SPLUNK_HEC_ENDPOINT=https://splunk.company.com:8088/services/collector
SPLUNK_HEC_TOKEN=your_token_here
```

### Step 4: Test Individual Modules

```bash
# Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# Test diagnostics
python src/diagnostics.py --ap_id YOUR_AP_ID --sle throughput

# Test remediation (use --force to skip guardrails for testing)
python src/remediation.py --ap_id YOUR_AP_ID --force

# Test validation
python src/validation.py --ap_id YOUR_AP_ID --sle throughput
```

---

## 🔧 GitHub Actions Setup

### Step 1: Add Repository Secrets

Go to: **Repository → Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Where to Get It |
|-------------|-----------------|
| `MIST_API_TOKEN` | Mist: Organization → Settings → API Tokens |
| `SITE_ID` | Mist: Organization → Sites (copy UUID from URL) |
| `ZENDESK_SUBDOMAIN` | Your Zendesk URL: `yourcompany.zendesk.com` → use `yourcompany` |
| `ZENDESK_EMAIL` | Email of automation account |
| `ZENDESK_API_TOKEN` | Zendesk: Admin → Apps & Integrations → APIs → Add API Token |
| `SPLUNK_HEC_ENDPOINT` | Splunk: Settings → Data Inputs → HTTP Event Collector |
| `SPLUNK_HEC_TOKEN` | Splunk: Create new HEC token |

### Step 2: Commit and Push

```bash
git add .
git commit -m "Initial deployment of Mist SLE automation"
git push origin main
```

### Step 3: Manually Test Workflow

1. Go to **Actions** tab in GitHub
2. Select **Mist SLE Proactive Automation**
3. Click **Run workflow**
4. Fill in:
   - **AP ID**: Your test AP ID
   - **SLE**: `throughput`
   - **Severity**: `high`
5. Click **Run workflow**
6. Watch the workflow execute!

---

## 📊 Expected Results

After running the workflow, you should see:

✅ **Zendesk**: New ticket created with `mist`, `automation` tags  
✅ **GitHub Actions**: Workflow completes successfully  
✅ **Artifacts**: `diagnostics.json`, `remediation.json`, `validation.json` available  
✅ **Splunk** (if configured): Audit events logged  

---

## 🎯 Next Steps

### For Production Deployment

1. **Tune Guardrails** (`rules/sle_rules.yaml`):
   ```yaml
   guardrails:
     min_clients: 5  # Increase for production
     min_reboot_interval: 3600  # 1 hour
   ```

2. **Configure Splunk Alert** (to auto-trigger workflow):
   - See: `docs/splunk_integration.md`
   - Set up saved search with webhook to GitHub Actions

3. **Set Up Monitoring**:
   - Splunk dashboard for MTTR metrics
   - Zendesk reports for automation success rate
   - GitHub Actions notifications

4. **Create Runbook**:
   - Document escalation procedures
   - Define on-call responsibilities
   - Test emergency shutdown

### For Developers

1. **Review Code Structure**:
   ```
   src/
   ├── mist.py          # Mist API client
   ├── diagnostics.py   # Health checks
   ├── remediation.py   # Remediation actions
   ├── validation.py    # SLE validation
   ├── zendesk.py       # Ticketing
   ├── splunk.py        # Audit logging
   └── logic.py         # Decision logic
   ```

2. **Run Tests**:
   ```bash
   pytest tests/ -v
   pytest --cov=src tests/
   ```

3. **Contribute**:
   - Fork repository
   - Create feature branch
   - Add tests
   - Submit pull request

---

## 📚 Key Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview and features |
| `PROJECT_SUMMARY.md` | Complete project summary |
| `docs/deployment_guide.md` | Step-by-step deployment |
| `docs/zendesk_integration.md` | Zendesk API details |
| `docs/splunk_integration.md` | Splunk HEC setup |
| `rules/sle_rules.yaml` | Configuration reference |

---

## 🐛 Troubleshooting

### "MIST_API_TOKEN not set"
**Solution**: Ensure secrets are configured in GitHub repository settings

### "Remediation blocked by guardrails"
**Solution**: Check diagnostics output for client count and AP uptime

### "Validation timeout"
**Solution**: Increase `max_attempts` in `rules/sle_rules.yaml`

### "Zendesk: Couldn't authenticate you"
**Solution**: Verify email format is `user@domain.com/token`

---

## 🎓 Learning Path

### Beginner
1. Read `README.md`
2. Run `quickstart.ps1`
3. Test individual modules locally
4. Review Zendesk tickets created

### Intermediate
1. Deploy to GitHub Actions
2. Configure Splunk integration
3. Tune guardrails and thresholds
4. Create custom dashboards

### Advanced
1. Extend remediation actions (WLAN reset, RRM)
2. Add multi-AP correlation
3. Implement machine learning for action selection
4. Contribute to project

---

## 💡 Pro Tips

1. **Start Small**: Test with 1-2 APs before site-wide deployment
2. **Monitor Closely**: Watch workflows for first week
3. **Tune Gradually**: Adjust guardrails based on results
4. **Document Changes**: Keep runbook updated
5. **Celebrate Wins**: Track MTTR reduction and share with team!

---

## 🆘 Getting Help

- **Documentation**: Check `docs/` folder first
- **GitHub Issues**: Open issue with logs and screenshots
- **Community**: Join discussions in repository
- **Professional Services**: Contact Juniper for advanced support

---

## ✅ Success Checklist

Before going to production:

- [ ] All secrets configured in GitHub
- [ ] Workflow tested successfully
- [ ] Guardrails tuned for your environment
- [ ] Monitoring dashboards created
- [ ] Team trained on runbook
- [ ] Escalation procedures documented
- [ ] Emergency shutdown tested
- [ ] Stakeholders notified

---

## 🎉 You're Ready!

Your Mist SLE automation pipeline is ready to:

✨ **Detect** SLE failures automatically  
✨ **Diagnose** AP health in seconds  
✨ **Remediate** safely with guardrails  
✨ **Validate** SLE restoration  
✨ **Track** everything in Zendesk  
✨ **Reduce MTTR** by up to 80%  

**Welcome to proactive network operations!** 🚀

---

*Need help? See documentation in `docs/` or open a GitHub issue.*
