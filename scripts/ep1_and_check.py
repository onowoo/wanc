# -*- coding: utf-8 -*-
"""导入第1集达标稿并通过后端校验，打印报告（迭代到达标）。"""
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


EP1 = """第1集 回乡
【内｜村口｜日】
秦昭背着旧药箱踏进村口，灰布衫发白，眉眼清冷。三个混混挡在路中。
混混甲：哟，这不是被赶出城的秦家小子？还敢回来？
秦昭：让开。
混混乙：让开？行——从哥几个胯下钻过去。
【动作】秦昭侧身要走，被混混乙一把攥住衣袖。
王强（踱下台阶，皮笑肉不笑）：秦大夫，稀客啊。这穷地方，可没人请你行医。
秦昭：我回自己的家。
王强：回家？你爹那破屋早抵给爷了。识相的，滚远点。
【动作】秦昭指节发白，只握紧药箱，没有发作。

【内｜巷口｜日】
一声哭喊，农妇抱着抽搐的孩子冲来。
农妇：救命！我娃吃了王大夫的药，快没气了！
王强（脸色一僵）：胡说！那是祖传秘方！
【动作】秦昭单膝跪地，搭上孩子的脉，指尖微凉，眼底掠过寒意。
秦昭：寒毒入心。你那"秘方"，掺了断肠草。
王强（挤出冷笑）：你少血口喷人！
【动作】秦昭取针，三针下去。孩子咳出一口黑血，缓缓睁眼。
众人：神了！秦家小子真有本事！
【动作】秦昭起身，从怀里摸出一张泛黄的药方残页——爷爷临终前塞给他的。
【本集钩子】：残页一角，那枚褪色的印记，竟与王强诊所门匾上的"祖传"印章，一模一样。
"""

if __name__ == "__main__":
    result = req("POST", f"/projects/{q()}/scripts/import", {
        "raw_text": EP1, "label": "第1集达标稿"})
    lines = [f"解析 {result['episode_count']} 集 | 质量分 {result['report']['score']} | {result['report']['summary']}"]
    for iss in result["report"]["issues"]:
        lines.append(f"  [{iss['severity']}] 第{iss.get('episode_index','')}集: {iss['message']} | 建议: {iss['suggestion']}")
    for e in result["episodes"]:
        lines.append(f"  第{e['index']}集 字数={e['word_count']} 钩子={'有' if e['hook'] else '无'}")
    out = "\n".join(lines)
    print(out)
    with open("E:/project/hongguo/wanc/scripts/ep1_report.txt", "w", encoding="utf-8") as f:
        f.write(out)
