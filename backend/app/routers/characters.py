# -*- coding: utf-8 -*-
"""人物路由：列表/新增/更新/删除 + 人设快照预览（渲染后注入 LLM 的文本）。"""
from fastapi import APIRouter, HTTPException

from ..models.character import Character, CharacterPayload
from ..services import character_service as cs

router = APIRouter(prefix="/api/projects/{project_id}/characters", tags=["characters"])


@router.get("")
def list_characters(project_id: str) -> list[Character]:
    try:
        return cs.list_characters(project_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@router.post("")
def add_character(project_id: str, payload: CharacterPayload) -> Character:
    try:
        return cs.add_character(project_id, payload)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@router.put("/{cid}")
def update_character(project_id: str, cid: str, payload: CharacterPayload) -> Character:
    try:
        return cs.update_character(project_id, cid, payload)
    except KeyError as e:
        raise HTTPException(404, str(e))


@router.delete("/{cid}")
def delete_character(project_id: str, cid: str) -> dict:
    try:
        cs.delete_character(project_id, cid)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    return {"deleted": cid}


@router.get("/snapshot")
def render_snapshot(project_id: str) -> dict:
    return {"snapshot": cs.render_character_snapshot(project_id)}
