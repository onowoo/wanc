# -*- coding: utf-8 -*-
"""提示词模板路由：列出模板 + 渲染完整 prompt（手动桥接模式核心）。"""
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from ..services import prompt_renderer

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


class RenderRequest(BaseModel):
    template_id: str = "submit_template"
    instruction: str = ""
    history_count: int = 0


@router.get("/templates")
def list_templates() -> list[dict]:
    return prompt_renderer.list_templates()


@router.post("/render/{project_id}")
def render(project_id: str, req: RenderRequest) -> dict:
    try:
        return prompt_renderer.render_prompt(
            project_id, req.template_id, req.instruction, req.history_count)
    except KeyError as e:
        raise HTTPException(404, str(e))
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
