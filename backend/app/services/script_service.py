# -*- coding: utf-8 -*-
"""剧本服务：读取/导入/更新分集，导入时自动解析 + 校验 + 版本快照。"""
from __future__ import annotations

from ..models.story import Episode, SceneBeat, Story
from ..models.validation import ValidationReport
from . import character_service as cs
from . import project_service as ps
from . import script_parser as parser
from . import validator as v
from . import versioning


def get_story(project_id: str) -> Story:
    data = ps.read_json(project_id, ps.SCRIPT_FILE)
    episodes = [Episode.model_validate(e) for e in data.get("episodes", [])]
    return Story(episodes=episodes)


def get_episodes(project_id: str) -> list[Episode]:
    return get_story(project_id).episodes


def import_text(project_id: str, raw_text: str, label: str = "导入") -> dict:
    """解析大模型返回文本 → 覆盖分集 → 校验 → 快照，返回结构化结果。"""
    episodes = parser.parse_script(raw_text)
    _persist_episodes(project_id, episodes)

    chars = cs.list_characters(project_id)
    report = v.validate_episodes(episodes, chars)
    versioning.snapshot(project_id, label or f"导入 {len(episodes)} 集")
    ps.touch(project_id)
    return {
        "episode_count": len(episodes),
        "episodes": [e.model_dump() for e in episodes],
        "report": report.model_dump(),
    }


def update_episode(project_id: str, index: int, title: str = "", beats: list[dict] | None = None,
                   source_text: str = "") -> Episode:
    episodes = get_episodes(project_id)
    ep = next((e for e in episodes if e.index == index), None)
    if ep is None:
        ep = Episode(index=index)
        episodes.append(ep)
        episodes.sort(key=lambda e: e.index)
    if title is not None:
        ep.title = title
    if beats is not None:
        ep.beats = [SceneBeat.model_validate(b) for b in beats]
    if source_text is not None:
        ep.source_text = source_text
        # 重算钩子
        hook = next((b.text for b in ep.beats if b.kind == "hook"), "")
        ep.hook = hook
    _persist_episodes(project_id, episodes)
    ps.touch(project_id)
    return ep


def set_outline(project_id: str, pitch: str = "", synopsis: str = "", outline: list[dict] | None = None) -> dict:
    data = {"pitch": pitch, "synopsis": synopsis, "outline": outline or []}
    ps.write_yaml(project_id, ps.OUTLINE_FILE, data)
    ps.touch(project_id)
    return data


def get_outline(project_id: str) -> dict:
    return ps.read_yaml(project_id, ps.OUTLINE_FILE)


def _persist_episodes(project_id: str, episodes: list[Episode]) -> None:
    ps.write_json(project_id, ps.SCRIPT_FILE, {"episodes": [e.model_dump() for e in episodes]})
