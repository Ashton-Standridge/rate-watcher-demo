"""Exchange-rate watcher: polls the free Frankfurter API (no key), logs to CSV, posts alerts to a webhook.

Run once (for cron / Task Scheduler / GitHub Actions) or loop with --every.
Webhook URL comes from config or the WEBHOOK_URL env var; with none set, alerts print to stdout (dry run).
"""
import argparse, csv, json, os, time
from datetime import datetime, timezone
from pathlib import Path
import requests

API = "https://api.frankfurter.app/latest"

def fetch_rates(base, symbols, get=requests.get):
    r = get(API, params={"from": base, "to": ",".join(symbols)}, timeout=15); r.raise_for_status()
    return r.json()["rates"]

def check(rules, rates):
    alerts = []
    for rule in rules:
        v = rates.get(rule["symbol"])
        if v is None: continue
        if "above" in rule and v > rule["above"]: alerts.append(f"{rule['symbol']} is {v} (above {rule['above']})")
        if "below" in rule and v < rule["below"]: alerts.append(f"{rule['symbol']} is {v} (below {rule['below']})")
    return alerts

def log(path, base, rates):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True); new = not p.exists()
    with open(p, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["timestamp_utc", "base", "symbol", "rate"])
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for s, v in rates.items(): w.writerow([ts, base, s, v])

def notify(url, base, alerts, post=requests.post):
    if not alerts: return "no alerts"
    text = f"Rate alert ({base} base):\n" + "\n".join(f"- {a}" for a in alerts)
    if not url: print("[dry run] would POST:\n" + text); return "dry run"
    post(url, json={"text": text, "content": text}, timeout=15).raise_for_status()  # works for Slack and Discord
    return "sent"

def run_once(cfg, get=requests.get, post=requests.post):
    syms = sorted({r["symbol"] for r in cfg["rules"]})
    rates = fetch_rates(cfg["base"], syms, get); log(cfg["history_csv"], cfg["base"], rates)
    alerts = check(cfg["rules"], rates)
    status = notify(os.environ.get("WEBHOOK_URL") or cfg.get("webhook_url"), cfg["base"], alerts, post)
    print(f"{datetime.now():%Y-%m-%d %H:%M} rates={rates} alerts={len(alerts)} webhook={status}")
    return rates, alerts

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="config.example.json"); ap.add_argument("--every", type=float, help="minutes between runs")
    a = ap.parse_args(argv); cfg = json.loads(Path(a.config).read_text())
    while True:
        try: run_once(cfg)
        except requests.RequestException as e: print("fetch failed, will retry next run:", e)
        if not a.every: break
        time.sleep(a.every * 60)

if __name__ == "__main__": main()
