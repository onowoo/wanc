# -*- coding: utf-8 -*-
"""剧本校验器：钩子、字数、开篇、敏感词、静态人设 OOC 提示。
静态规则优先，可独立于 LLM 运行；后续可加 LLM 深度 OOC 校验。"""
from __future__ import annotations

from ..models.character import Character
from ..models.story import Episode
from ..models.validation import Issue, ValidationReport

MIN_WORDS = 300
MAX_WORDS = 500

# 基础敏感词黑名单（简化版，真实审核还需人工复核 + 平台正式规则）
SENSITIVE_PATTERNS = [
    "赌博", "高利贷", "裸贷", "涉政", "军警", "宗教", "封建迷信",
    "强买强卖", "虚假医疗", "包治百病", "性别对立", "仇富",
]


def validate_episodes(episodes: list[Episode], characters: list[Character] | None = None) -> ValidationReport:
    issues: list[Issue] = []
    if not episodes:
        return ValidationReport(issues=[Issue(severity="error", code="no_episodes", message="没有解析到任何剧集")], score=0)

    characters = characters or []
    score = 100

    for ep in episodes:
        idx = ep.index
        # 1) 钩子检查
        if not ep.hook and not _has_hook_beat(ep):
            issues.append(Issue(
                severity="error", code="missing_hook",
                episode_index=idx,
                message=f"第{idx}集缺少结尾钩子",
                suggestion="在结尾增加『【本集钩子】：...』，停在即将揭晓的悬念节点",
            ))
            score -= 8
        # 2) 字数检查
        wc = ep.word_count
        if wc and wc < MIN_WORDS:
            issues.append(Issue(severity="warning", code="word_count_low",
                                episode_index=idx, message=f"第{idx}集字数 {wc}，低于 {MIN_WORDS}",
                                suggestion="内容偏单薄，补充冲突拉扯细节"))
            score -= 2
        elif wc > MAX_WORDS:
            issues.append(Issue(severity="warning", code="word_count_high",
                                episode_index=idx, message=f"第{idx}集字数 {wc}，高于 {MAX_WORDS}",
                                suggestion="压缩台词与动作，单集控制在 300-500 字"))
            score -= 2
        # 3) 敏感词
        for pat in SENSITIVE_PATTERNS:
            if pat in ep.source_text:
                issues.append(Issue(severity="error", code="sensitive",
                                    episode_index=idx, message=f"第{idx}集命中敏感词：{pat}",
                                    suggestion="删除/改写相关内容，避免违规下架"))
                score -= 10
        # 4) 静态人设 OOC 提示（弱校验：禁止行为关键词出现在台词/动作中）
        for ch in characters:
            for fb in ch.forbidden_behavior:
                if not fb.strip():
                    continue
                kw = fb.strip().split("，")[0][:6]
                if kw and kw in ep.source_text:
                    issues.append(Issue(severity="warning", code="ooc",
                                        episode_index=idx,
                                        message=f"第{idx}集疑似触发『{ch.name}』禁止行为：{fb}",
                                        suggestion="核对是否违背该人物人设红线"))

    # 5) 开篇铺垫检查（第1集，启发式）
    if episodes:
        first = episodes[0]
        head = first.source_text[:120]
        if any(k in head for k in ["小时候", "回忆", "从小", "那年", "从前", "背景介绍", "身世交代"]):
            issues.append(Issue(severity="warning", code="slow_open",
                                episode_index=first.index,
                                message="第1集开头疑似大段背景/回忆铺垫",
                                suggestion="短剧前 8 秒必须直抛绝境冲突，删除铺垫"))
            score -= 3

    score = max(0, score)
    if score >= 90:
        summary = "整体质量良好"
    elif score >= 70:
        summary = "存在需修复问题，重点看钩子与字数"
    else:
        summary = "存在较多硬伤，建议按告警逐项修复后再投稿/生成"

    return ValidationReport(issues=issues, score=score, summary=summary)


def _has_hook_beat(ep: Episode) -> bool:
    return any(b.kind == "hook" for b in ep.beats)
