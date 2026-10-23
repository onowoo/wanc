# -*- coding: utf-8 -*-
"""导出30集完整投稿包（调用后端 /exports/markdown）。"""
import json
import urllib.parse
import urllib.request

PID = "演示_神级医仙"
BASE = "http://127.0.0.1:8000/api"
r = urllib.request.Request(BASE + f"/projects/{urllib.parse.quote(PID)}/export/markdown", method="GET")
with urllib.request.urlopen(r) as resp:
    data = json.loads(resp.read().decode("utf-8"))
print(json.dumps(data, ensure_ascii=False, indent=2))
