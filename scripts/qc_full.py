# -*- coding: utf-8 -*-
"""整体质量检查：拉取全部30集 + 人设，逐集过校验器，统计字数/钩子/告警/人设一致性。"""
import json
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, "E:/project/hongguo/wanc/backend")
from app.models.character import Character  # noqa: E402
from app.models.story import Episode  # noqa: E402
from app.services.validator import validate_episodes, diagnose_opening  # noqa: E402

PID = "演示_神级医仙"
BASE = "http://127.0.0.1:8000/api"


def req(method, path):
    r = urllib.request.Request(BASE + path, method=method)
    with urllib.request.urlopen(r) as resp:
        return json.loads(resp.read().decode("utf-8"))


def q():
    return urllib.parse.quote(PID)


def main():
    ep_dicts = req("GET", f"/projects/{q()}/scripts")["episodes"]
    ch_dicts = req("GET", f"/projects/{q()}/characters")
    proj = req("GET", f"/projects/{q()}")
    episodes = [Episode.model_validate(d) for d in ep_dicts]
    characters = [Character.model_validate(d) for d in ch_dicts]

    episodes.sort(key=lambda e: e.index)
    report = validate_episodes(episodes, characters, target_count=proj.get("target_episodes"))

    print(f"总集数: {len(episodes)}")
    print(f"质量分: {report.score} | {report.summary}")
    print("== 逐集 ==")
    for ep in episodes:
        print(f"第{ep.index:>2}集 字数={ep.word_count:>3} 钩子={'有' if ep.hook else '无'}")
    print("== 告警 ==")
    if not report.issues:
        print("无告警 ✅")
    for iss in report.issues:
        print(f"[{iss.severity}] 第{iss.episode_index}集: {iss.message}")

    # 人设一致性统计
    print("== 人设一致性抽查 ==")
    qin_lines = [l for e in episodes for l in e.beats
                 if l.kind == "line" and l.speaker and l.speaker.startswith("秦昭")]
    qin_len = [len(l.text) for l in qin_lines]
    avg = sum(qin_len) / len(qin_len) if qin_len else 0
    print(f"秦昭台词 {len(qin_len)} 句，平均 {avg:.1f} 字/句（说话风格=话少而稳，宜短）")
    short = sum(1 for n in qin_len if n <= 16)
    print(f"其中 ≤16字 短句 {short} 句（{short*100//len(qin_len)}%）")

    # 王强禁止行为"当众失态"核对：正文不得出现王强当众失控
    wang_ooc = []
    for ep in episodes:
        for beat in ep.beats:
            t = getattr(beat, "text", "") or ""
            if "王强" in t and any(k in t for k in ["跌坐", "瘫", "跪地求饶", "嚎啕", "鼻涕"]):
                wang_ooc.append((ep.index, t))
    print(f"王强'不当众失态'核对: {'发现疑似失控 ' + str(wang_ooc) if wang_ooc else '未见（符合人设红线）'}")

    # 钩子连贯抽查：每集钩子是否指向下集冲突（抽查3处）
    print("== 钩子-下集衔接抽查 ==")
    for idx in [1, 10, 20]:
        if idx <= len(episodes):
            print(f"第{idx}集钩子: {episodes[idx-1].hook[:40]}...")

    # 开篇爆点诊断（第1集专项）
    print("== 开篇爆点诊断（第1集）==")
    opening = diagnose_opening(episodes)
    for d in opening["dims"]:
        mark = "✅" if d["hit"] else "❌"
        ev = "、".join(d["words"]) if d["hit"] else "缺失"
        print(f"{mark} {d['label']}: {ev}")
    print(f"开篇爆点评分: {opening['score']}/{opening['total']}")
    if opening["missing"]:
        print(f"缺项: {'、'.join(opening['missing'])} → 建议强化后重写第1集")
    else:
        print("六项爆点要素全部到位 ✅")


if __name__ == "__main__":
    main()
