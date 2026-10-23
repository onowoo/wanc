# -*- coding: utf-8 -*-
"""剧本数据模型：卖点、梗概、大纲、分集脚本。"""
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class SceneBeat(BaseModel):
    """单条剧本行：场景头 / 动作 / 台词。"""
    kind: str = Field(description="block 类型：scene|action|line|hook|meta")
    text: str = ""
    speaker: Optional[str] = None


class Episode(BaseModel):
    index: int = Field(description="集数，从 1 开始")
    title: str = ""
    beats: list[SceneBeat] = Field(default_factory=list)
    source_text: str = Field(default="", description="该集原始文本（便于溯源）")
    hook: str = Field(default="", description="本集结尾钩子（解析时提取）")

    @computed_field
    @property
    def word_count(self) -> int:
        return len(self.source_text)


class OutlineItem(BaseModel):
    """分集大纲条目。"""
    index: int
    summary: str = ""
    node_type: str = Field(default="", description="节点类型：小打脸/中型反转/马甲曝光/大反转/普通")


class Story(BaseModel):
    """一个完整剧本工程的内容资产。"""
    pitch: str = Field(default="", description="一句话卖点（≤30字）")
    synopsis: str = Field(default="", description="故事梗概 150-250 字")
    characters_meta: dict[str, str] = Field(default_factory=dict, description="简易人物卡（投稿用）")
    outline: list[OutlineItem] = Field(default_factory=list)
    episodes: list[Episode] = Field(default_factory=list)


class OutlinePayload(BaseModel):
    pitch: str = ""
    synopsis: str = ""
    outline: list[OutlineItem] = []
