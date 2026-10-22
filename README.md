# Scheduled API Watcher with Webhook Alerts

[![tests](https://github.com/Ashton-Standridge/rate-watcher-demo/actions/workflows/tests.yml/badge.svg)](https://github.com/Ashton-Standridge/rate-watcher-demo/actions/workflows/tests.yml)
[![rate-watch](https://github.com/Ashton-Standridge/rate-watcher-demo/actions/workflows/watch.yml/badge.svg)](https://github.com/Ashton-Standridge/rate-watcher-demo/actions/workflows/watch.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.12-blue.svg)

> **Sample / demo project.** Not client work. It uses the free, public [Frankfurter API](https://www.frankfurter.app/) (no API key).

Checks currency exchange rates on a schedule, logs every reading to CSV, and posts one alert to a Slack- or Discord-style webhook when a rate crosses a threshold you set. The same pattern works for prices, stock levels or any JSON API.

![Sample run in dry-run mode](screenshot.svg)

## The problem
People want to know when a number changes without checking a website all day. This is the small, reliable script that watches for them.

## Sample output
```text
$ python watcher.py
[dry run] would POST:
Rate alert (USD base):
- EUR is 0.89246 (above 0.8)
- JPY is 157.05 (above 140)
2026-10-22 14:57 rates={'EUR': 0.89246, 'GBP': 0.74761, 'JPY': 157.05} alerts=2 webhook=dry run
```
Rules live in [`config.example.json`](config.example.json):
```json
{"base": "USD", "rules": [{"symbol": "EUR", "above": 0.80}, {"symbol": "GBP", "below": 0.70}, {"symbol": "JPY", "above": 140}]}
```

## Features
- `above` / `below` thresholds per symbol in a JSON file.
- Appends every reading to `output/history.csv` for later charts.
- One combined alert per run to `WEBHOOK_URL` (an environment variable, so no secrets in the repo). With no URL set, it runs as a dry run and prints the alert.
- Run once (cron, Windows Task Scheduler, GitHub Actions) or loop with `--every 60`.
- [`watch.yml`](.github/workflows/watch.yml) runs it hourly on GitHub Actions, reading the webhook from a repository secret.
- Network calls are injectable, so tests use a fake API response and a real local mock webhook server.

## Quickstart
```bash
git clone https://github.com/Ashton-Standridge/rate-watcher-demo.git
cd rate-watcher-demo
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python watcher.py                                   # one run, dry run
WEBHOOK_URL=https://hooks.example/... python watcher.py --every 60
```
To get alerts from the hourly workflow, add a `WEBHOOK_URL` repository secret (Settings → Secrets and variables → Actions).

## Project layout
```text
watcher.py                    fetch -> log -> check rules -> alert (CLI entry point)
config.example.json           thresholds and settings
test_watcher.py               pytest suite (fake API + local mock webhook)
.github/workflows/tests.yml   runs the tests on every push
.github/workflows/watch.yml   runs the watcher hourly
output/run.txt                log of a real run
```

## Tests
```bash
python -m pytest -q
```
Runs on every push in [GitHub Actions](https://github.com/Ashton-Standridge/rate-watcher-demo/actions/workflows/tests.yml).

## How this maps to client work
| If you need… | This demo shows… |
|---|---|
| A ping when a price, stock level or metric changes | Threshold rules against any JSON API |
| Alerts in Slack, Discord or your own system | Webhook posting with a dry-run mode |
| Something that runs without a server | Cron, Task Scheduler or GitHub Actions |
| Keys kept out of code | Secrets from environment variables |

## Need this for your data?
Want an alert or a scheduled job for your API, store or spreadsheet? [Message me on Upwork](https://www.upwork.com/freelancers/~01d2f0883f3e7f03a4). More samples: [https://ashton-standridge.github.io/](https://ashton-standridge.github.io/)

## License
[MIT](LICENSE) © 2026 Ashton Standridge (Venture Studio Arts)
