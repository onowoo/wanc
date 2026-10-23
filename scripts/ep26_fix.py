# -*- coding: utf-8 -*-
"""修正第26集王强失态（瘫坐在地→强撑门面），符合'不当众失态'人设红线。"""
import json
import urllib.parse
import urllib.request

PID = "演示_神级医仙"
BASE = "http://127.0.0.1:8000/api"


def req(method, path, payload=None):
    url = BASE + path
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    r = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(r) as resp:
        return json.loads(resp.read().decode("utf-8"))


def q():
    return urllib.parse.quote(PID)


E26 = """第26集 反水
【内｜县衙大堂｜日】
县令升堂，秦昭呈上铁证：毒药材、投毒伙计、旧案卷宗、残页印痕。
县令：王强，你作何解释？
王强（强撑）：大人！这都是秦昭栽赃！何掌柜可以作证，我药铺里从来没有毒药！
【动作】话音刚落，何掌柜被人带上堂来，面如土色。
何掌柜（噗通跪下）：大人！小人招了！是王强指使小人供毒药，往井里下毒，还要栽赃秦大夫！小人有账册为证！
【动作】王强脸色骤白，一把扶住桌沿，强撑着没有倒下。
王强（咬牙，强作镇定）：何守财！你、你竟敢反我！你莫要血口喷人！
何掌柜：王强，我不反你，死的就是我。你那点毒药害人的勾当，我可一件没落，都记着呢！
【动作】王强额角青筋直跳，却死死撑着，不肯在堂上跌了颜面。
【本集钩子】：县令拍下惊堂木：将王强、何掌柜收监候审！堂下百姓一片叫好，秦昭却看向人群后的钱师爷——那人正一点点往门口缩。
"""

if __name__ == "__main__":
    result = req("POST", f"/projects/{q()}/scripts/import", {
        "raw_text": E26, "label": "第26集OOC修正"})
    for e in result["episodes"]:
        print(f"第{e['index']}集 字数={e['word_count']} 钩子={'有' if e['hook'] else '无'} 分={result['report']['score']}")
    for iss in result["report"]["issues"]:
        print(f"  [{iss['severity']}] 第{iss.get('episode_index','')}集: {iss['message']}")
    print("完成")
