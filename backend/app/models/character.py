# -*- coding: utf-8 -*-
"""人物模型：人设一致性的一等公民，结构化实体而非自由文本。"""
from typing import Literal, Optional

from pydantic import BaseModel, Field

RoleType = Literal["protagonist", "antagonist", "ally", "tool"]


class Character(BaseModel):
    cid: str = Field(description="人物唯一 id，如 c001")
    name: str
    role_type: RoleType = "tool"
    core_desire: str = Field(default="", description="核心欲望")
    core_weakness: str = Field(default="", description="核心弱点")
    personality_tags: list[str] = Field(default_factory=list, description="性格标签")
    speech_style: str = Field(default="", description="说话风格")
    forbidden_behavior: list[str] = Field(default_factory=list, description="禁止行为（人设红线）")
    appearance_desc: str = Field(default="", description="固定外貌描述，用于漫剧绘图提示词/投稿")
    relations: dict[str, str] = Field(default_factory=dict, description="与其它 cid 的关系描述")

    def to_prompt_block(self) -> str:
        """渲染成注入 LLM 的强约束人设文本。"""
        lines = [
            f"人物：{self.name}（角色类型：{self.role_type}）",
            f"- 核心欲望：{self.core_desire or '未设定'}",
            f"- 核心弱点：{self.core_weakness or '未设定'}",
        ]
        if self.personality_tags:
            lines.append(f"- 性格标签：{'、'.join(self.personality_tags)}")
        if self.speech_style:
            lines.append(f"- 说话风格：{self.speech_style}")
        if self.forbidden_behavior:
            lines.append(f"- 禁止行为（绝对不能出现）：{'；'.join(self.forbidden_behavior)}")
        if self.appearance_desc:
            lines.append(f"- 固定外貌：{self.appearance_desc}")
        if self.relations:
            rel_txt = "；".join(f"{k}：{v}" for k, v in self.relations.items())
            lines.append(f"- 人物关系：{rel_txt}")
        return "\n".join(lines)


class CharacterPayload(BaseModel):
    name: str
    role_type: RoleType = "tool"
    core_desire: str = ""
    core_weakness: str = ""
    personality_tags: list[str] = []
    speech_style: str = ""
    forbidden_behavior: list[str] = []
    appearance_desc: str = ""
    relations: dict[str, str] = {}
