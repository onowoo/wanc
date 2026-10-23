# -*- coding: utf-8 -*-
"""导出模块：Markdown 投稿包 / 结构化 JSON，兼容红果编剧投稿与未来视频流水线。"""
from __future__ import annotations

from datetime import datetime

from ..models.story import Episode, Story
from . import character_service as cs
from . import project_service as ps


def build_markdown(project_id: str) -> str:
    meta = ps.get_project(project_id)
    outline = ps.read_yaml(project_id, ps.OUTLINE_FILE)
    chars = cs.list_characters(project_id)
    story = Story(episodes=get_episodes_impl(project_id))

    lines: list[str] = []
    lines.append(f"# {meta.name}")
    lines.append("")
    if meta.genre:
        lines.append(f"> 题材：{meta.genre}　|　赛道：{meta.track}　|　目标集数：{meta.target_episodes}")
        lines.append("")
    # 集数完整性：目标集数 vs 实际集数（投稿级事故，审稿第一页即卡）
    if meta.target_episodes and len(story.episodes) < meta.target_episodes:
        lines.append(f"> ⚠ 目标 {meta.target_episodes} 集，当前正文仅 {len(story.episodes)} 集，投稿前需补齐或核对目标集数")
        lines.append("")

    lines.append("## 一句话卖点")
    lines.append(outline.get("pitch", "") or "（未填写）")
    lines.append("")

    lines.append("## 故事梗概")
    lines.append(outline.get("synopsis", "") or "（未填写）")
    lines.append("")

    lines.append("## 人物卡")
    if chars:
        for c in chars:
            lines.append(f"### {c.name}（{c.role_type}）")
            lines.append(f"- 核心欲望：{c.core_desire or '未设定'}")
            lines.append(f"- 核心弱点：{c.core_weakness or '未设定'}")
            if c.personality_tags:
                lines.append(f"- 性格标签：{'、'.join(c.personality_tags)}")
            if c.speech_style:
                lines.append(f"- 说话风格：{c.speech_style}")
            if c.forbidden_behavior:
                lines.append(f"- 禁止行为：{'；'.join(c.forbidden_behavior)}")
            lines.append("")
    else:
        lines.append("（未填写）")
        lines.append("")

    ol = outline.get("outline", [])
    if ol:
        lines.append("## 分集大纲")
        for item in ol:
            tag = f"[{item.get('node_type', '')}]" if item.get("node_type") else ""
            lines.append(f"- 第{item.get('index', '?')}集{tag}：{item.get('summary', '')}")
        lines.append("")

    lines.append("## 分集正文")
    if story.episodes:
        for ep in story.episodes:
            lines.append(f"### 第{ep.index}集 {ep.title}".rstrip())
            lines.append("")
            lines.append(_render_episode_text(ep))
    else:
        lines.append("（暂无分集正文）")

    return "\n".join(lines)


def get_episodes_impl(project_id: str) -> list[Episode]:
    from . import script_service
    return script_service.get_episodes(project_id)


def _render_episode_text(ep: Episode) -> str:
    if ep.source_text:
        return ep.source_text
    # 用 beats 重建
    parts = []
    for b in ep.beats:
        if b.kind == "scene":
            parts.append(f"【{b.text}】")
        elif b.kind == "action":
            parts.append(f"动作描述：{b.text}")
        elif b.kind == "line":
            parts.append(f"{b.speaker}：{b.text}")
        elif b.kind == "hook":
            parts.append(f"【本集钩子】：{b.text}")
        else:
            parts.append(b.text)
    return "\n".join(parts)


def export_markdown_file(project_id: str) -> dict:
    meta = ps.get_project(project_id)
    content = build_markdown(project_id)
    d = ps.ensure_project(project_id)
    exports = d / ps.EXPORTS_DIR
    exports.mkdir(exist_ok=True)
    safe = meta.name.replace("/", "_").replace("\\", "_") or meta.id
    path = exports / f"{safe}_投稿包_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path.write_text(content, encoding="utf-8")
    return {"path": str(path), "filename": path.name, "content": content}


def export_json(project_id: str) -> dict:
    meta = ps.get_project(project_id)
    outline = ps.read_yaml(project_id, ps.OUTLINE_FILE)
    story = get_episodes_impl(project_id)
    return {
        "project": meta.model_dump(),
        "outline": outline,
        "characters": [c.model_dump() for c in cs.list_characters(project_id)],
        "episodes": [e.model_dump() for e in story],
    }
