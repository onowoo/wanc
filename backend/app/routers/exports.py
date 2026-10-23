# -*- coding: utf-8 -*-
"""导出路由：Markdown 投稿包 / JSON 结构化脚本。"""
from fastapi import APIRouter, HTTPException

from ..services import exporter

router = APIRouter(prefix="/api/projects/{project_id}/export", tags=["exports"])


@router.get("/markdown")
def export_markdown(project_id: str) -> dict:
    try:
        return exporter.export_markdown_file(project_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@router.get("/markdown/raw")
def export_markdown_raw(project_id: str) -> dict:
    try:
        return {"content": exporter.build_markdown(project_id)}
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@router.get("/json")
def export_json(project_id: str) -> dict:
    try:
        return exporter.export_json(project_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
