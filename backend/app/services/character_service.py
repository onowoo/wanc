# -*- coding: utf-8 -*-
"""人物服务：读写字幕，生成注入 LLM 的「人设快照文本」（人设一致性核心）。"""
from __future__ import annotations

from ..config import CHARACTERS_FILE
from ..models.character import Character, CharacterPayload
from . import project_service as ps


def list_characters(project_id: str) -> list[Character]:
    data = ps.read_yaml(project_id, CHARACTERS_FILE)
    raw = data.get("characters", [])
    return [Character.model_validate(c) for c in raw]


def get_character(project_id: str, cid: str) -> Character:
    for c in list_characters(project_id):
        if c.cid == cid:
            return c
    raise KeyError(f"人物不存在：{cid}")


def next_cid(characters: list[Character]) -> str:
    n = len(characters) + 1
    while any(c.cid == f"c{n:03d}" for c in characters):
        n += 1
    return f"c{n:03d}"


def add_character(project_id: str, payload: CharacterPayload) -> Character:
    chars = list_characters(project_id)
    char = Character(
        cid=next_cid(chars),
        name=payload.name,
        role_type=payload.role_type,
        core_desire=payload.core_desire,
        core_weakness=payload.core_weakness,
        personality_tags=payload.personality_tags,
        speech_style=payload.speech_style,
        forbidden_behavior=payload.forbidden_behavior,
        appearance_desc=payload.appearance_desc,
        relations=payload.relations,
    )
    chars.append(char)
    _save(project_id, chars)
    return char


def update_character(project_id: str, cid: str, payload: CharacterPayload) -> Character:
    chars = list_characters(project_id)
    for c in chars:
        if c.cid == cid:
            c.name = payload.name or c.name
            c.role_type = payload.role_type
            c.core_desire = payload.core_desire
            c.core_weakness = payload.core_weakness
            c.personality_tags = payload.personality_tags
            c.speech_style = payload.speech_style
            c.forbidden_behavior = payload.forbidden_behavior
            c.appearance_desc = payload.appearance_desc
            c.relations = payload.relations
            _save(project_id, chars)
            return c
    raise KeyError(f"人物不存在：{cid}")


def delete_character(project_id: str, cid: str) -> None:
    chars = [c for c in list_characters(project_id) if c.cid != cid]
    _save(project_id, chars)


def _save(project_id: str, chars: list[Character]) -> None:
    ps.write_yaml(project_id, CHARACTERS_FILE, {"characters": [c.model_dump() for c in chars]})
    ps.touch(project_id)


def render_character_snapshot(project_id: str) -> str:
    """把所有人物渲染成一段强约束文本，注入 prompt，从源头锁死人设。"""
    chars = list_characters(project_id)
    if not chars:
        return "（本项目暂未设定人物，请先补全人物设定以保证人设一致性。）"
    blocks = [c.to_prompt_block() for c in chars]
    return "\n\n".join(blocks)
