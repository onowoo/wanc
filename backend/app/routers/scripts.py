# -*- coding: utf-8 -*-
"""剧本路由：获取分集、导入解析、更新单集、校验报告、版本管理。"""
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from ..models.story import Episode
from ..services import script_service
from ..services import validator as v
from ..services import versioning
from ..services import character_service as cs

router = APIRouter(prefix="/api/projects/{project_id}/scripts", tags=["scripts"])


class ImportRequest(BaseModel):
    raw_text: str
    label: str = "导入"


class EpisodeUpdate(BaseModel):
    title: str = ""
    beats: list[dict] | None = None
    source_text: str = ""


@router.get("")
def get_script(project_id: str) -> dict:
    return {"episodes": [e.model_dump() for e in script_service.get_episodes(project_id)]}


@router.post("/import")
def import_text(project_id: str, req: ImportRequest) -> dict:
    if not req.raw_text.strip():
        raise HTTPException(400, "raw_text 为空")
    return script_service.import_text(project_id, req.raw_text, req.label)


@router.post("/validate")
def validate(project_id: str) -> dict:
    episodes = script_service.get_episodes(project_id)
    chars = cs.list_characters(project_id)
    return v.validate_episodes(episodes, chars).model_dump()


@router.put("/episode/{index}")
def update_episode(project_id: str, index: int, req: EpisodeUpdate) -> Episode:
    try:
        return script_service.update_episode(
            project_id, index, title=req.title, beats=req.beats, source_text=req.source_text)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


# ---- 版本 ----
@router.get("/versions")
def list_versions(project_id: str) -> list[dict]:
    return versioning.list_versions(project_id)


@router.post("/versions")
def create_version(project_id: str, payload: dict) -> dict:
    return {"version": versioning.snapshot(project_id, payload.get("label", "手动快照"))}


@router.post("/versions/{version}/restore")
def restore(project_id: str, version: str) -> dict:
    try:
        return versioning.restore(project_id, version)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@router.get("/versions/{version_a}/diff/{version_b}")
def diff(project_id: str, version_a: str, version_b: str) -> dict:
    return {"diff": versioning.diff(project_id, version_a, version_b)}
