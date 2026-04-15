# Security Newspaper 📰

A lightweight, daily security news aggregator that fetches from 10 curated cybersecurity sources, classifies articles into 7 sections, and publishes a newspaper-formatted message to Slack.


## Quick Start

### 1. Clone and Setup

```bash
git clone <repo>
cd security-newspaper
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Configure Slack Webhook

Get your Slack Incoming Webhook URL:
1. Go to https://api.slack.com/apps
2. Create a new app or select existing one
3. Enable Incoming Webhooks
4. Create new webhook URL and copy it

Set environment variable:
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### 3. Test Immediately

```bash
python -m src.main --now
```

This will:
- Fetch from all 10 sources
- Classify articles into 7 sections
- Format and send to Slack
- Show output in terminal + logs

### 4. Schedule Daily Runs

Edit your crontab:
```bash
crontab -e
```

Add (runs every weekday at 8 AM):
```
0 8 * * 1-5 cd /path/to/security-newspaper && /path/to/venv/bin/python -m src.main
```

Check logs:
```bash
tail -f logs/newspaper.log
```

## Configuration

Edit `config.yaml`:

- **schedule**: Cron expression, timezone, lookback hours
- **slack**: Webhook URL (via env var), newspaper name
- **sources**: 10 RSS feeds (enable/disable, weights)
- **sections**: Category keywords (emoji, regex patterns)

Example:
```yaml
schedule:
  cron: "0 8 * * 1-5"       # Every weekday 8 AM
  timezone: "Europe/Berlin"
  lookback_hours: 24
  max_items_per_section: 5

slack:
  webhook_url: "${SLACK_WEBHOOK_URL}"  # Set via env var
```

## Command Line Options

```bash
python -m src.main [OPTIONS]

Options:
  --now           Run pipeline immediately (don't schedule)
  --test          Use mock RSS sources for testing
  --dry-run       Format and display but don't publish to Slack
  --config FILE   Path to config.yaml
```

### Examples

```bash
# Run now and publish to Slack
python -m src.main --now

# Test with mock sources (doesn't hit real feeds)
python -m src.main --now --test

# Dry-run: format but don't send to Slack
python -m src.main --now --dry-run

# Start daemon (scheduled via cron)
python -m src.main
```

## Architecture

```
┌─────────────────────────────────────┐
│ 10 RSS Sources                      │
├─────────────────────────────────────┤
│ Fetcher (parallel ThreadPoolExecutor)
├─────────────────────────────────────┤
│ Deduplicator (session hash)         │
├─────────────────────────────────────┤
│ Classifier (regex → 7 sections)     │
├─────────────────────────────────────┤
│ Formatter (Slack Block Kit)         │
├─────────────────────────────────────┤
│ Publisher (Webhook → Slack Channel) │
└─────────────────────────────────────┘
```

### Modules

- `config.py` - YAML configuration loader & validator
- `fetcher.py` - Parallel RSS feed fetcher (ThreadPoolExecutor)
- `deduplicator.py` - Session-only deduplication (in-memory hash)
- `classifier.py` - Article classification by regex keywords
- `formatter.py` - Slack Block Kit JSON formatting
- `publisher.py` - Webhook POST to Slack
- `orchestrator.py` - Pipeline orchestration
- `main.py` - CLI & APScheduler daemon

## Slack Gazette Format

Message contains:
- Header with date, total stories, source count
- 7 sections (emoji + section name):
  - ⚠️ Threat Intelligence
  - 🐛 Vulnerabilities & CVEs
  - 🚨 Data Breaches
  - 💀 Ransomware & Malware
  - 🏛️ Industry & Policy
  - 🔧 Tools & Techniques
  - 📢 Advisories
- Per-article: title (linked), description snippet, source
- Footer with generation timestamp

## 10 Security Sources

1. **CISA Alerts** - Government advisories
2. **Krebs on Security** - Breach investigations
3. **Schneier on Security** - Policy & analysis
4. **SANS ISC** - Daily threat summary
5. **The Hacker News** - Critical vulnerabilities
6. **Bleeping Computer** - Ransomware & malware
7. **Dark Reading** - Enterprise security
8. **SecurityWeek** - CVE announcements
9. **Recorded Future** - APT & threat intel
10. **CERT/CC** - Vulnerability advisories

## Logs

Logs written to `logs/newspaper.log`:
- INFO: Fetch summary, classification summary, publish status
- DEBUG: Per-article details, regex matches
- ERROR: Failed fetches, configuration errors

```bash
# Watch logs in real-time
tail -f logs/newspaper.log

# Check for errors
grep ERROR logs/newspaper.log
```


## Troubleshooting

### No articles appear in gazette

```bash
# Check for fetch errors
tail -f logs/newspaper.log | grep ERROR

# Test with mock sources
python -m src.main --now --test

# Check RSS source URLs in config.yaml
```

### Slack message not posting

```bash
# Verify webhook URL is set
echo $SLACK_WEBHOOK_URL

# Test webhook directly
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test"}' \
  $SLACK_WEBHOOK_URL

# Check logs for HTTP errors
tail -f logs/newspaper.log | grep "Slack"
```

### Wrong section assignments

Edit regex keywords in `config.yaml` sections, restart.

### Schedule not triggering

Verify cron job:
```bash
crontab -l
```

Check system log:
```bash
log show --predicate 'eventMessage contains "newspaper"' --last 1h
```

## Development

### Project Structure

```
security-newspaper/
├── config.yaml              # Configuration
├── requirements.txt         # Dependencies
├── src/
│   ├── __init__.py
│   ├── main.py             # Entry point & CLI
│   ├── config.py           # Config loader
│   ├── models.py           # Data classes
│   ├── fetcher.py          # RSS fetcher
│   ├── deduplicator.py     # Dedup logic
│   ├── classifier.py       # Section classification
│   ├── formatter.py        # Slack formatting
│   ├── publisher.py        # Slack publishing
│   └── orchestrator.py     # Pipeline
├── test/
│   ├── __init__.py
│   └── mock_sources.py     # Mock RSS data
└── logs/
    └── newspaper.log       # Runtime logs
```

## License

MIT License - See LICENSE file

---
