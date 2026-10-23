# -*- coding: utf-8 -*-
"""HTTP 全链路冒烟测试（urllib，处理中文 URL/JSON 干净）。"""
import json
import urllib.parse
import urllib.request

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


def main():
    name = f"HTTP测试_重生长公主_{__import__('time').strftime('%H%M%S')}"
    proj = req("POST", "/projects", {
        "name": name, "genre": "女频逆袭", "track": "重生复仇",
        "target_episodes": 40, "purpose": "submit", "template": "submit_template"})
    pid = proj["id"]
    print(f"[1] 创建项目 OK id={pid}")

    req("POST", f"/projects/{urllib.parse.quote(pid)}/characters", {
        "name": "陆昭", "role_type": "protagonist", "core_desire": "夺回储君之位，手刃叛徒",
        "core_weakness": "重情念旧", "personality_tags": ["冷峻", "隐忍", "杀伐果断"],
        "speech_style": "寡言，出口即定论", "forbidden_behavior": ["不会当众失态", "不会放过背刺者"],
        "appearance_desc": "玄衣玉冠，眉眼锋锐"})
    req("POST", f"/projects/{urllib.parse.quote(pid)}/characters", {
        "name": "苏澈", "role_type": "antagonist", "core_desire": "篡位夺权",
        "personality_tags": ["阴鸷", "多疑"]})
    chars = req("GET", f"/projects/{urllib.parse.quote(pid)}/characters")
    print(f"[2] 新增人物 OK 共 {len(chars)} 人：{[c['name'] for c in chars]}")

    prompt = req("POST", f"/prompts/render/{urllib.parse.quote(pid)}", {
        "template_id": "submit_template", "instruction": "生成前2集完整正文", "history_count": 0})
    assert "陆昭" in prompt["full_prompt"] and "禁止行为" in prompt["full_prompt"]
    print(f"[3] 渲染 prompt OK 长度 {len(prompt['full_prompt'])} 字，人设已注入")

    sample = """第1集 归朝
【内｜御书房｜日】
陆昭负手而立，冷眼扫过龙椅前的众人。
苏澈：殿下，您该让贤了。
陆昭：夺我储位，你配？
【本集钩子】：门外传来兵甲碰撞声，一封密旨递到陆昭手中。
"""
    imp = req("POST", f"/projects/{urllib.parse.quote(pid)}/scripts/import", {
        "raw_text": sample, "label": "HTTP导入"})
    print(f"[4] 导入剧本 OK 集数={imp['episode_count']} 质量分={imp['report']['score']}")
    for e in imp["episodes"]:
        print(f"     第{e['index']}集 钩子={e['hook']}")

    md = req("GET", f"/projects/{urllib.parse.quote(pid)}/export/markdown")
    print(f"[5] 导出投稿包 OK {md['filename']} 长度 {len(md['content'])}")

    versions = req("GET", f"/projects/{urllib.parse.quote(pid)}/scripts/versions")
    print(f"[6] 版本快照 {len(versions)} 个：{versions[0]['version']}")

    req("DELETE", f"/projects/{urllib.parse.quote(pid)}")
    print("[7] 已清理测试项目")
    print("==== HTTP 全链路测试通过 ====")


if __name__ == "__main__":
    main()
