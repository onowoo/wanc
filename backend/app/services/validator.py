# -*- coding: utf-8 -*-
"""剧本校验器：钩子、字数、开篇、敏感词、静态人设 OOC，及审稿级一致性规则。
静态规则优先，可独立于 LLM 运行；后续可加 LLM 深度 OOC 校验。"""
from __future__ import annotations

import re

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

# 审稿级规则常量
# 户外场景若误标【内】，剧组无法开拍（村口/巷口/广场/山道/街道/桥/井/集市/路口/门外/野外等）
OUTDOOR_KEYWORDS = ["村口", "巷口", "广场", "山道", "街道", "长街", "集市", "路口", "门外", "院外",
                    "野外", "山路", "桥头", "井边", "村", "坡", "巷", "街", "田埂", "田间"]
# 室内词：命中则即使含户外词也不算误标（如「村口茶馆」实为室内）
INDOOR_KEYWORDS = ["茶馆", "店内", "店中", "馆", "铺", "堂", "屋", "宅", "府", "楼", "间", "房", "室内"]
# 小说化心理/神态/眼神叙述词：分镜脚本中应改写为外部可见动作
NOVEL_NARRATION = ["眼底", "眸色", "眸中", "心头", "心中", "暗暗", "眼神", "目光", "神色",
                   "嘴角", "眉心", "心头一", "心中一动", "眼底掠过", "眸色微动", "心头剧震"]
MIN_LINE_RATIO = 0.35  # 台词字数 / 总字数，低于则提示叙述过重
_SCENE_RE = re.compile(r"【(内|外)｜[^｜】]+｜[日夜晚]】")


def _scene_marks(source: str):
    """提取所有场景行（如【内｜村口｜日】），返回 match 迭代器。"""
    return _SCENE_RE.finditer(source)


def validate_episodes(episodes: list[Episode], characters: list[Character] | None = None,
                      target_count: int | None = None) -> ValidationReport:
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

        # 5) 场景内外合理性：户外地点误标【内】＝剧组开不了工的低级错误
        for m in _scene_marks(ep.source_text):
            pos = m.group(0)
            if pos.startswith("【内") and any(k in pos for k in OUTDOOR_KEYWORDS) \
                    and not any(i in pos for i in INDOOR_KEYWORDS):
                issues.append(Issue(
                    severity="warning", code="scene_inout",
                    episode_index=idx,
                    message=f"第{idx}集户外场景误标【内】：{pos}",
                    suggestion="村口/巷口/广场/山道/街道等室外场景应标【外】，室内才标【内】"))
                score -= 2
                break  # 每集只报一次，避免刷屏

        # 6) 台词密度：台词占比过低＝小说化叙述过重，偏离可拍分镜
        if ep.word_count:
            line_words = sum(len(b.text) for b in ep.beats if b.kind == "line")
            ratio = line_words / ep.word_count
            if ratio < MIN_LINE_RATIO:
                issues.append(Issue(
                    severity="warning", code="line_density",
                    episode_index=idx,
                    message=f"第{idx}集台词密度 {ratio:.0%}，低于建议 {MIN_LINE_RATIO:.0%}",
                    suggestion="动作/叙述偏小说化，增加外部动作与对白拉扯，靠近可拍分镜"))
                score -= 2

        # 7) 小说化心理/神态/眼神叙述：分镜应改外部可见动作
        novel_hits = [k for k in NOVEL_NARRATION
                      if any(b.kind == "meta" and k in b.text for b in ep.beats)]
        if novel_hits:
            issues.append(Issue(
                severity="warning", code="novel_narration",
                episode_index=idx,
                message=f"第{idx}集含小说化叙述词：{'、'.join(novel_hits[:4])}",
                suggestion="【动作】里避免心理/眼神/神态描写，改写为可拍的外部动作（如攥拳、移开视线、顿步）"))
            score -= 2

        # 8) 重复功能角色提示（设定冗余：两个同职能配角）
        if idx in (16, 30) and "赵叔" in ep.source_text and "师叔" in ep.source_text:
            issues.append(Issue(
                severity="warning", code="redundant_role",
                episode_index=idx,
                message="同集出现『赵叔』『师叔』两个功能相似的老伙计，疑似设定冗余",
                suggestion="合并为一个角色，避免两个同职能配角同时存在"))

        # 9) 集数完整性：实际集数 < 目标集数（投稿级事故，审稿第一页即卡）
        if target_count is not None and idx == episodes[-1].index and len(episodes) < target_count:
            issues.append(Issue(
                severity="warning", code="target_mismatch",
                episode_index=idx,
                message=f"目标 {target_count} 集，实际仅 {len(episodes)} 集",
                suggestion="补齐缺失集数，或将项目目标集数改为实际集数，保持一致"))

    # 10) 开篇铺垫检查（第1集，启发式）
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
