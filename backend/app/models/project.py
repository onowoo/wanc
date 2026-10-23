# -*- coding: utf-8 -*-
"""项目元数据模型。"""
from typing import Literal, Optional

from pydantic import BaseModel, Field

PurposeType = Literal["submit", "draft"]  # submit=投稿版，draft=漫剧草稿版


class ProjectMeta(BaseModel):
    id: str
    name: str
    genre: str = Field(default="", description="题材标签")
    track: str = Field(default="", description="目标赛道：女频逆袭/男频神医等")
    target_episodes: int = Field(default=40, ge=1, le=200)
    purpose: PurposeType = "submit"
    template: str = Field(default="submit_template", description="选中的 prompt 模板 id")
    llm_notes: str = Field(default="", description="备注/预留 LLM 参数")
    created_at: str = ""
    updated_at: str = ""


class ProjectCreate(BaseModel):
    name: str
    genre: str = ""
    track: str = ""
    target_episodes: int = 40
    purpose: PurposeType = "submit"
    template: str = "submit_template"
