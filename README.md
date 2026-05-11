<div align="center">
  <h1>Security Newspaper 📰</h1>
  <p><strong>A daily security news aggregator that keeps your team informed.</strong></p>
  <p>Automatically fetches cybersecurity articles from 13 verified working sources, organizes them into 7 categories, and delivers a polished newspaper to your Slack channel each morning.</p>
  <br>
  <a href="#features">Features</a> &bull; <a href="#installation">Installation</a> &bull; <a href="#usage">Usage</a> &bull; <a href="#configuration">Configuration</a> &bull; <a href="#troubleshooting">Troubleshooting</a> &bull; <a href="#contributing">Contributing</a>
  <br><br>
</div>

---

## Features

- 🔍 **Multi-Source Aggregation** – Fetches from 13 verified working security sources in parallel
- 📂 **Auto-Categorization** – Organizes articles into 7 security categories with emoji
- 🚫 **Deduplication** – Removes duplicate articles from the same day
- 📰 **Slack-Ready Format** – Professional newspaper layout for Slack delivery
- ⏰ **Flexible Scheduling** – Run daily via system cron or on-demand
- 📊 **Rich Logging** – Detailed activity logs for debugging and monitoring
- ⚙️ **Fully Configurable** – Customize sources, categories, timing via `config.yaml`

---

## Installation

### Prerequisites

- **Python 3.8+**
- **Slack Workspace** with webhook capability
- **Internet Connection** for fetching RSS feeds

### Step 1: Clone & Setup

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
5. Export as environment variable:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

> [!TIP]
> Save this to your shell profile (`.bashrc`, `.zshrc`, etc.) to persist across sessions.

### Step 3: Test It Works

```bash
python -m src.main --now
```

Expected output:
- Articles fetched from 13 sources ✓
- Articles organized into 7 sections ✓
- Newspaper message posted to Slack ✓
- Logs saved to `logs/newspaper.log` ✓

### Step 4: Schedule Daily Delivery (Recommended)

Set up automatic daily runs using system cron:

```bash
crontab -e
```

Add this line (runs every weekday at 9 AM):

```bash
0 9 * * 1-5 cd /path/to/security-newspaper && SLACK_WEBHOOK_URL="your-webhook-url" /path/to/venv/bin/python -m src.main --now >> logs/cron.log 2>&1
```

Verify the cron job:

```bash
crontab -l | grep security-newspaper
```

> [!NOTE]
> **System cron is recommended over the Python daemon mode** for reliability. It ensures the job continues running indefinitely without process crashes or state accumulation issues.

---

## Usage

### Command Reference

```bash
# Run immediately (don't wait for schedule)
python -m src.main --now

# Test with fake data (doesn't hit real feeds)
python -m src.main --now --test

# Preview output without sending to Slack
python -m src.main --now --dry-run

# Use a different config file
python -m src.main --config custom-config.yaml

# Start background daemon (not recommended for production)
python -m src.main
```

### Monitor Activity

```bash
# Watch logs in real-time
tail -f logs/newspaper.log

# Check for errors
grep ERROR logs/newspaper.log

# Search for specific source
grep "BleepingComputer" logs/newspaper.log
```

---

## Configuration

All settings are in `config.yaml`. Most defaults work, but you can customize:

### Basic Settings

```yaml
schedule:
  cron: "0 9 * * 1-5"       # Runs every weekday at 9 AM
  timezone: "Europe/Berlin"  # Your timezone
  lookback_hours: 24        # Fetch articles from last 24 hours
  max_items_per_section: 5  # Max articles per category

slack:
  webhook_url: "${SLACK_WEBHOOK_URL}"   # Read from environment
  newspaper_name: "Security Gazette"    # Name shown in Slack
  show_sources_count: true              # Display source count in header
```

### News Sources

**13 Verified & Active Sources:**

| Tier | Source | Description |
|------|--------|-------------|
| **Government** | CISA Alerts | US government cybersecurity advisories |
| **Security Research** | Krebs on Security | Deep-dive breach investigations |
| **Security Research** | Recorded Future | Advanced threat intelligence |
| **Security Research** | Microsoft Security Blog | Microsoft security advisories & research |
| **Enterprise Security** | SANS ISC | Daily threat summaries & analysis |
| **Enterprise Security** | Dark Reading | Enterprise security news |
| **Enterprise Security** | CrowdStrike Blog | Threat intelligence & incident response |
| **Threat Intelligence** | Bleeping Computer | Malware, ransomware & security news |
| **Threat Intelligence** | Threatpost | Vulnerability & threat analysis |
| **Threat Intelligence** | Help Net Security | Cybersecurity research & insights |
| **Tech & General** | TechCrunch Security | Breaking tech security incidents |
| **Tech & General** | Ars Technica | In-depth tech & security analysis |
| **Executive News** | CSO Online | Chief Security Officer news & trends |

> [!NOTE]
> All 13 sources are tested, active, and verified to fetch articles regularly.

### Categories

Customize keywords and emoji for the 7 security categories in `config.yaml`:

- 🔍 **Threat Intelligence** – APT activity, security research
- 🐛 **Vulnerabilities** – CVE announcements, exploits
- 🚨 **Data Breaches** – Corporate breaches, incidents
- 💀 **Ransomware & Malware** – New malware families, campaigns
- 🏛️ **Industry & Policy** – Regulations, government updates
- 🔧 **Tools & Techniques** – New security tools, methods
- 📢 **Advisories** – Security patches, recommendations

---

## How It Works

The system follows this pipeline:

```
Fetch Articles (13 sources) → Deduplicate → Categorize 
    ↓
Format for Slack → Send to Webhook → Log Results
```

**Process:**
1. **Fetch** – Downloads articles from 13 RSS feeds simultaneously
2. **Deduplicate** – Removes articles already sent today
3. **Classify** – Organizes into 7 security categories using keywords
4. **Format** – Converts to Slack-readable newspaper layout
5. **Publish** – Sends message to Slack webhook
6. **Log** – Records all activity for troubleshooting

---

## Project Structure

```
security-newspaper/
├── config.yaml              # Main configuration
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── src/                    # Application code
│   ├── main.py            # Entry point & CLI
│   ├── config.py          # Config loader
│   ├── models.py          # Data structures
│   ├── fetcher.py         # Fetch articles
│   ├── deduplicator.py    # Remove duplicates
│   ├── classifier.py      # Categorize articles
│   ├── formatter.py       # Format for Slack
│   ├── publisher.py       # Send to Slack
│   └── orchestrator.py    # Run pipeline
│
├── test/                  # Testing utilities
│   ├── mock_sources.py    # Fake articles for testing
│   └── __init__.py
│
└── logs/                  # Runtime logs
    └── newspaper.log      # Main log file
```

**Technologies:**
- `APScheduler` – Handles scheduled runs
- `feedparser` – Parses RSS feeds
- `requests` – Sends to Slack
- `PyYAML` – Reads configuration

---

## Troubleshooting

### ❌ No Articles in the Newspaper

**Check what's happening:**
```bash
python -m src.main --now --dry-run
tail -f logs/newspaper.log | grep ERROR
```

**Try test mode:**
```bash
python -m src.main --now --test
```

**Verify sources:**
- Is each source enabled in `config.yaml`?
- Is your internet connection working?
- Are the RSS URLs accessible (not blocked)?

### ❌ Message Not Appearing in Slack

**Verify webhook:**
```bash
echo $SLACK_WEBHOOK_URL
# Should print: https://hooks.slack.com/services/...
```

**Test webhook directly:**
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message"}' \
  $SLACK_WEBHOOK_URL
```

**Check logs:**
```bash
tail -f logs/newspaper.log | grep -i "slack"
```

### ❌ Articles in Wrong Categories

1. Open `config.yaml`
2. Find the `sections` area
3. Update keywords and regex patterns
4. Test with `python -m src.main --now --dry-run`

### ❌ Scheduled Job Not Running

**Verify cron is set:**
```bash
crontab -l
```

**Check system logs (macOS):**
```bash
log show --predicate 'eventMessage contains "newspaper"' --last 1h
```

**Test manually:**
```bash
cd /path/to/security-newspaper && python -m src.main --now
```

**Note:** System cron may not inherit environment variables. Ensure `SLACK_WEBHOOK_URL` is set in the cron entry or passed via `.env` file.

---

## Contributing

We welcome contributions! Please help improve Security Newspaper.

**For major features:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Open an Issue for:**
- 🐛 Bug reports or code problems
- ✨ Feature requests
- ❓ Questions or usage clarification
- 💡 Minor improvements or suggestions

---

## FAQ

**Q: Can I add my own news source?**  
A: Yes! Add the RSS feed URL to `config.yaml` in the `sources` section.

**Q: How often can it run?**  
A: As often as you want. Adjust the cron expression in `config.yaml`. Default is weekdays at 9 AM.

**Q: Does it remove duplicates across different days?**  
A: No, duplicates are only removed within the same day by design.

**Q: Can I customize categories?**  
A: Yes! Edit the `sections` in `config.yaml` to add, remove, or modify categories and keywords.

**Q: What Python versions are supported?**  
A: Python 3.8+. Check your version with `python --version`.

---

## License

[MIT License](LICENSE) – See LICENSE file for details.

---

**Have questions?** Check logs with `tail -f logs/newspaper.log` or open an [Issue](../../issues).
