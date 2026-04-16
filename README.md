# Security Newspaper 📰

**A daily security news aggregator that keeps your team informed.**

Automatically fetches cybersecurity articles from 10 trusted sources, organizes them into 7 categories, and delivers a polished newspaper to your Slack channel each morning.

---

## ✨ What It Does

- 🔍 Fetches articles from 10 security sources in parallel
- 📂 Automatically categorizes articles into 7 sections
- 🚫 Removes duplicate articles from the same day
- 📰 Formats a professional newspaper for Slack
- ⏰ Runs automatically on a daily schedule
- 📋 Logs all activities for troubleshooting

---

## 🚀 Quick Start (5 minutes)

### Step 1: Setup Python Environment

```bash
git clone <repo>
cd security-newspaper
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Create Slack Webhook

1. Go to https://api.slack.com/apps
2. Click "Create New App" (or select existing)
3. Enable "Incoming Webhooks"
4. Create a new webhook and copy the URL
5. Save it as an environment variable:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Step 3: Test It Works

```bash
python -m src.main --now
```

You should see:
- Articles fetched from 10 sources ✓
- Articles organized into 7 sections ✓
- A newspaper message posted to Slack ✓
- Logs saved to `logs/newspaper.log` ✓

### Step 4: Schedule Daily Delivery

Set up automatic daily runs:

```bash
crontab -e
```

Add this line (runs every weekday at 8 AM):
```
0 8 * * 1-5 cd /path/to/security-newspaper && /path/to/venv/bin/python -m src.main
```

Monitor the logs anytime:
```bash
tail -f logs/newspaper.log
```

---

## ⚙️ Configuration

All settings are in `config.yaml`. Most defaults work out of the box, but you can customize:

**Basic Settings:**
```yaml
schedule:
  cron: "0 8 * * 1-5"       # Runs every weekday at 8 AM
  timezone: "Europe/Berlin"  # Your timezone
  lookback_hours: 24        # How far back to look for articles
  max_items_per_section: 5  # Max articles per category

slack:
  webhook_url: "${SLACK_WEBHOOK_URL}"  # Read from environment variable
  newspaper_name: "Security Gazette"   # Name shown in Slack
```

**News Sources:** Enable/disable each of the 10 sources in the config
**Categories:** Customize keywords and emoji for each of the 7 sections

---

## 💻 Commands Reference

### Common Commands

```bash
# Run immediately (don't wait for schedule)
python -m src.main --now

# Test with fake data (doesn't hit real news sites)
python -m src.main --now --test

# Preview output without sending to Slack
python -m src.main --now --dry-run

# Use a different config file
python -m src.main --config custom-config.yaml

# Start background daemon (uses cron schedule)
python -m src.main
```

---

## 🏗️ How It Works

The system follows this pipeline:

```
10 News Sources → Fetch Articles → Remove Duplicates → Categorize 
    ↓
Format for Slack → Send to Slack → Log Results
```

**Step by Step:**

1. **Fetch** - Pulls articles from 10 RSS feeds simultaneously
2. **Deduplicate** - Removes articles already sent today
3. **Classify** - Organizes articles into 7 security categories
4. **Format** - Converts to a Slack-readable newspaper layout
5. **Publish** - Sends to your Slack webhook
6. **Log** - Records everything for troubleshooting

---

## 📦 Project Modules

| Module | Purpose |
|--------|---------|
| `main.py` | Entry point and command-line interface |
| `config.py` | Loads and validates settings from `config.yaml` |
| `fetcher.py` | Downloads articles from RSS feeds in parallel |
| `deduplicator.py` | Prevents duplicate articles in the daily digest |
| `classifier.py` | Assigns articles to security categories |
| `formatter.py` | Converts articles to Slack message format |
| `publisher.py` | Sends the message to Slack via webhook |
| `orchestrator.py` | Manages the complete pipeline |
| `models.py` | Data structures used throughout |

---

## 📰 The Slack Newspaper Format

Here's what the daily message includes:

**Header**
- Date and time generated
- Total number of articles
- Number of sources used

**7 News Sections** (each with emoji):
| Section | Emoji | Content |
|---------|-------|---------|
| Threat Intelligence | 🔍 | APT activity, security research |
| Vulnerabilities | 🐛 | CVE announcements, exploits |
| Data Breaches | 🚨 | Corporate breaches, incidents |
| Ransomware & Malware | 💀 | New malware families, campaigns |
| Industry & Policy | 🏛️ | Regulations, government updates |
| Tools & Techniques | 🔧 | New security tools, methods |
| Advisories | 📢 | Security patches, recommendations |

**Per Article**
- Title (clickable link to original)
- Brief description
- Source name

**Footer**
- Generation timestamp

---

## 📡 The 10 News Sources

1. **CISA Alerts** - US government security advisories
2. **Krebs on Security** - Deep-dive breach investigations
3. **Schneier on Security** - Policy analysis and commentary
4. **SANS ISC** - Daily threat summaries
5. **The Hacker News** - Critical vulnerabilities
6. **Bleeping Computer** - Ransomware and malware focus
7. **Dark Reading** - Enterprise security news
8. **SecurityWeek** - CVE and vulnerability news
9. **Recorded Future** - Advanced threat intelligence
10. **CERT/CC** - Official vulnerability advisories

---

## 📋 Logs & Debugging

All activity is logged to `logs/newspaper.log`:

**Log Levels:**
- `INFO` - Successful runs, fetch summaries, publish confirmations
- `DEBUG` - Per-article details, regex matches, detailed processing
- `ERROR` - Failed fetches, configuration errors, connection issues

**Watch logs live:**
```bash
tail -f logs/newspaper.log
```

**Find problems:**
```bash
# Look for errors
grep ERROR logs/newspaper.log

# Check Slack connection
grep "Slack" logs/newspaper.log

# See articles from a specific source
grep "BleepingComputer" logs/newspaper.log
```


---

## 🔧 Troubleshooting

### ❌ No articles in the newspaper

**Check what's happening:**
```bash
python -m src.main --now --dry-run
tail -f logs/newspaper.log | grep ERROR
```

**Try the test mode:**
```bash
# Uses fake data instead of real feeds
python -m src.main --now --test
```

**Verify RSS sources are available:**
- Check `config.yaml` - are sources enabled?
- Verify internet connection
- Check that RSS URLs are not blocked

---

### ❌ Message not appearing in Slack

**Verify webhook is set correctly:**
```bash
# Check environment variable
echo $SLACK_WEBHOOK_URL

# Should print: https://hooks.slack.com/services/...
```

**Test the webhook directly:**
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message"}' \
  $SLACK_WEBHOOK_URL
```

**Check logs for errors:**
```bash
tail -f logs/newspaper.log | grep -i "slack"
```

---

### ❌ Articles in wrong categories

**Fix categorization:**
1. Open `config.yaml`
2. Find the `sections` area
3. Update keywords and regex patterns
4. Restart the application

---

### ❌ Scheduled job not running

**Verify cron is set up:**
```bash
# List your cron jobs
crontab -l
```

**Check system logs (macOS):**
```bash
log show --predicate 'eventMessage contains "newspaper"' --last 1h
```

**Test the cron command manually:**
```bash
cd /path/to/security-newspaper && /path/to/venv/bin/python -m src.main
```

---

## 👨‍💻 Development & Project Structure

**Directory layout:**
```
security-newspaper/
├── config.yaml              # Main configuration file
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── src/                    # Main application code
│   ├── main.py            # Entry point & CLI
│   ├── config.py          # Config loader
│   ├── models.py          # Data structures
│   ├── fetcher.py         # Fetch articles
│   ├── deduplicator.py    # Remove duplicates
│   ├── classifier.py      # Categorize articles
│   ├── formatter.py       # Format for Slack
│   ├── publisher.py       # Send to Slack
│   └── orchestrator.py    # Run the pipeline
│
├── test/                   # Testing utilities
│   ├── mock_sources.py    # Fake articles for testing
│   └── __init__.py
│
└── logs/                   # Runtime logs
    └── newspaper.log      # Main log file
```

**Key technologies:**
- `APScheduler` - Handles scheduled runs
- `feedparser` - Parses RSS feeds
- `requests` - Sends to Slack
- `PyYAML` - Reads configuration

---

## ❓ FAQ

**Q: Can I add my own news source?**
A: Yes! Add the RSS feed URL to `config.yaml` in the `sources` section.

**Q: How often can I run it?**
A: As often as you want. Adjust the cron expression in `config.yaml`. Default is weekdays at 8 AM.

**Q: Does it remove duplicates across different days?**
A: No, duplicates are only removed within the same day. This is by design.

**Q: Can I change the categories?**
A: Yes. Edit the `sections` in `config.yaml` to add, remove, or modify categories.

**Q: What Python version do I need?**
A: Python 3.8 or newer. Check your version with `python --version`.

---

## 📄 License

MIT License - See LICENSE file for details

---

**Have questions?** Check the logs with `tail -f logs/newspaper.log` or review the troubleshooting section above.
