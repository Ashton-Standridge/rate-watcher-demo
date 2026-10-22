import json, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests, watcher

class R:
    def __init__(s, d): s.d = d
    def raise_for_status(s): pass
    def json(s): return s.d

CFG = {"base": "USD", "rules": [{"symbol": "EUR", "above": 0.8}, {"symbol": "GBP", "below": 0.7}], "webhook_url": ""}

def test_check():
    assert watcher.check(CFG["rules"], {"EUR": 0.9, "GBP": 0.75}) == ["EUR is 0.9 (above 0.8)"]

def test_run_with_mock_webhook(tmp_path, monkeypatch):
    got = []
    class H(BaseHTTPRequestHandler):
        def do_POST(s):
            got.append(json.loads(s.rfile.read(int(s.headers["Content-Length"])))); s.send_response(204); s.end_headers()
        def log_message(s, *a): pass
    srv = HTTPServer(("127.0.0.1", 0), H); threading.Thread(target=srv.handle_request, daemon=True).start()
    monkeypatch.delenv("WEBHOOK_URL", raising=False)
    cfg = {**CFG, "webhook_url": f"http://127.0.0.1:{srv.server_port}/hook", "history_csv": str(tmp_path/"h.csv")}
    _, alerts = watcher.run_once(cfg, get=lambda *a, **k: R({"rates": {"EUR": 0.9, "GBP": 0.6}}), post=requests.post)
    srv.server_close()
    assert len(alerts) == 2 and "EUR is 0.9" in got[0]["text"]
    assert len((tmp_path/"h.csv").read_text().splitlines()) == 3
