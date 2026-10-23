# -*- coding: utf-8 -*-
"""校验告警模型。"""
from typing import Literal, Optional

from pydantic import BaseModel, Field

Severity = Literal["error", "warning", "info"]


class Issue(BaseModel):
    severity: Severity = "warning"
    code: str = Field(description="规则码，如 missing_hook / word_count / ooc")
    message: str
    episode_index: Optional[int] = None
    suggestion: str = ""


class ValidationReport(BaseModel):
    issues: list[Issue] = []
    score: int = Field(default=100, ge=0, le=100, description="剧本质量分（校验规则扣分制）")
    summary: str = ""
