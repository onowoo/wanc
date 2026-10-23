# -*- coding: utf-8 -*-
"""提示词模板渲染引擎：加载 yaml skill 模板，注入人设快照/梗概/大纲/历史集，产出完整 prompt。"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from ..config import TEMPLATE_DIR
from . import character_service as cs
from . import project_service as ps


@dataclass
class Template:
    id: str
    name: str
    description: str
    system_prompt: str
    user_prompt: str


def _load_all() -> list[Template]:
    templates = []
    for path in sorted(TEMPLATE_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        templates.append(
            Template(
                id=data.get("id", path.stem),
                name=data.get("name", path.stem),
                description=data.get("description", ""),
                system_prompt=data.get("system_prompt", ""),
                user_prompt=data.get("user_prompt", ""),
            )
        )
    return templates


def list_templates() -> list[dict]:
    return [
        {"id": t.id, "name": t.name, "description": t.description}
        for t in _load_all()
    ]


def get_template(template_id: str) -> Template:
    for t in _load_all():
        if t.id == template_id:
            return t
    raise KeyError(f"模板不存在：{template_id}")


def _render_outline_block(project_id: str) -> str:
    data = ps.read_yaml(project_id, ps.OUTLINE_FILE)
    pitch = data.get("pitch", "")
    synopsis = data.get("synopsis", "")
    outline = data.get("outline", [])
    lines = []
    if pitch:
        lines.append(f"一句话卖点：{pitch}")
    if synopsis:
        lines.append(f"故事梗概：{synopsis}")
    if outline:
        lines.append("分集大纲：")
        for item in outline:
            idx = item.get("index", "")
            node = item.get("node_type", "")
            tag = f"[{node}]" if node else ""
            lines.append(f"  第{idx}集{tag}：{item.get('summary', '')}")
    if not lines:
        return "（暂未填写卖点/梗概/大纲，请在生成前补充，或用一句话点子在本轮指令中说明。）"
    return "\n".join(lines)


def _render_history_block(project_id: str, history_count: int) -> str:
    if history_count <= 0:
        return "（暂无已写剧集。）"
    data = ps.read_json(project_id, ps.SCRIPT_FILE)
    episodes = data.get("episodes", [])
    if not episodes:
        return "（暂无已写剧集。）"
    recent = episodes[-history_count:]
    parts = []
    for ep in recent:
        idx = ep.get("index", "?")
        title = ep.get("title", "")
        src = ep.get("source_text", "")
        parts.append(f"===== 第{idx}集 {title} =====\n{src}")
    return "\n\n".join(parts)


def render_prompt(project_id: str, template_id: str, instruction: str, history_count: int = 0) -> dict:
    """返回完整渲染结果。"""
    template = get_template(template_id)
    characters = cs.render_character_snapshot(project_id)
    outline = _render_outline_block(project_id)
    history = _render_history_block(project_id, history_count)

    def _fill(tpl: str) -> str:
        return (
            tpl.replace("{{characters}}", characters)
            .replace("{{outline}}", outline)
            .replace("{{history_episodes}}", history)
            .replace("{{instruction}}", instruction or "生成剧本")
        )

    system_prompt = _fill(template.system_prompt)
    user_prompt = _fill(template.user_prompt)
    return {
        "template_id": template.id,
        "template_name": template.name,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "full_prompt": system_prompt + "\n\n===== 用户指令 =====\n" + user_prompt,
    }
