# -*- coding: utf-8 -*-
"""剧本文本解析器：把大模型返回的原始文本，解析成结构化分集对象。
与 LLM 来源（豆包桌面端 / 未来 API）解耦，均可复用同一套解析。"""
from __future__ import annotations

import re

from ..models.story import Episode, SceneBeat

# 集分隔标记：第X集 / EP X / == X == / —X— 等
_EP_SPLIT = re.compile(
    r"(?m)^\s*(?:第\s*(\d{1,3})\s*集|EP\s*[:：]?\s*(\d{1,3})|===\s*第?\s*(\d{1,3})\s*集?\s*===|—\s*(\d{1,3})\s*—)\s*[:：]?\s*(.*)$"
)
# 场景行：【内/外｜地点｜日/夜】
_SCENE = re.compile(r"^\s*【(.+?)(?:[｜|](.+?))?】\s*$")
# 钩子标记：支持 "本集钩子：" 与 "【本集钩子】："
_HOOK = re.compile(r"^\s*【?\s*(?:本集钩子|钩子|片尾钩子|结尾钩子)\s*】?\s*[:：]\s*(.*)$", re.I)
# 动作/描述标记
_ACTION = re.compile(r"^\s*(?:动作描述|动作|画面)\s*[:：]\s*(.*)$")
# 台词：角色名：内容（角色名不包含冒号）
_LINE = re.compile(r"^\s*([^:：]{1,12})\s*[:：]\s*(.+)$")


def parse_script(raw_text: str) -> list[Episode]:
    """解析整篇剧本文本为分集列表。"""
    if not raw_text or not raw_text.strip():
        return []
    raw_text = raw_text.strip()

    # 1) 切分集
    matches = list(_EP_SPLIT.finditer(raw_text))
    episodes: list[Episode] = []

    if not matches:
        # 无显式集标记：整段视为 1 集
        episodes.append(_parse_one_episode(1, "", raw_text))
        return episodes

    for i, m in enumerate(matches):
        num = next((g for g in m.groups() if g), None)
        index = int(num) if num else i + 1
        title = (m.group(5) or "").strip()
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        body = raw_text[start:end]
        episodes.append(_parse_one_episode(index, title, body))
    return episodes


def _parse_one_episode(index: int, title: str, body: str) -> Episode:
    beats: list[SceneBeat] = []
    hook = ""
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # 跳过集标题行本身
        if _EP_SPLIT.match(line):
            continue
        beat = _classify_line(line)
        beats.append(beat)
        if beat.kind == "hook":
            hook = beat.text
    # source_text 为原始正文（去掉集标题行）
    source_text = "\n".join(
        ln.strip() for ln in body.splitlines() if ln.strip() and not _EP_SPLIT.match(ln.strip())
    )
    return Episode(index=index, title=title, beats=beats, source_text=source_text, hook=hook)


def _classify_line(line: str) -> SceneBeat:
    # 钩子
    hm = _HOOK.match(line)
    if hm:
        return SceneBeat(kind="hook", text=hm.group(1).strip())
    # 场景
    sm = _SCENE.match(line)
    if sm:
        scene = sm.group(1).strip()
        sub = sm.group(2).strip() if sm.group(2) else ""
        text = f"{scene}{'｜' + sub if sub else ''}"
        return SceneBeat(kind="scene", text=text)
    # 动作
    am = _ACTION.match(line)
    if am:
        return SceneBeat(kind="action", text=am.group(1).strip())
    # 台词
    lm = _LINE.match(line)
    if lm:
        speaker, content = lm.group(1).strip(), lm.group(2).strip()
        if speaker not in ("动作", "描述", "画面", "场景"):
            return SceneBeat(kind="line", speaker=speaker, text=content)
    # 其它（元信息/旁白/章节）
    return SceneBeat(kind="meta", text=line)
