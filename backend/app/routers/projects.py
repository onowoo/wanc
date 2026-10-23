# -*- coding: utf-8 -*-
"""项目路由：列表/创建/详情/更新/删除 + 大纲读写。"""
from fastapi import APIRouter, HTTPException

from ..models.project import ProjectCreate, ProjectMeta
from ..services import project_service as ps
from ..services import script_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("")
def list_projects() -> list[ProjectMeta]:
    return ps.list_projects()


@router.post("")
def create_project(payload: ProjectCreate) -> ProjectMeta:
    try:
        return ps.create_project(payload)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{project_id}")
def get_project(project_id: str) -> ProjectMeta:
    try:
        return ps.get_project(project_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@router.put("/{project_id}")
def update_project(project_id: str, payload: ProjectCreate) -> ProjectMeta:
    try:
        return ps.update_project(project_id, payload)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@router.delete("/{project_id}")
def delete_project(project_id: str) -> dict:
    try:
        ps.delete_project(project_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    return {"deleted": project_id}


@router.get("/{project_id}/outline")
def get_outline(project_id: str) -> dict:
    return script_service.get_outline(project_id)


@router.put("/{project_id}/outline")
def put_outline(project_id: str, payload: dict) -> dict:
    try:
        return script_service.set_outline(
            project_id,
            pitch=payload.get("pitch", ""),
            synopsis=payload.get("synopsis", ""),
            outline=payload.get("outline", []),
        )
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
