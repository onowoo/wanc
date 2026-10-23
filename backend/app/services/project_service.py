# -*- coding: utf-8 -*-
"""项目管理与存储：每个剧本工程 = storage/<id>/ 目录下的 yaml/json 资产。"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import yaml

from ..config import (
    CHARACTERS_FILE,
    EXPORTS_DIR,
    OUTLINE_FILE,
    PROJECT_FILE,
    SCRIPT_FILE,
    STORAGE_DIR,
    VERSIONS_DIR,
)
from ..models.project import ProjectCreate, ProjectMeta

_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\u4e00-\u9fa5]{1,64}$")


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def slugify(name: str) -> str:
    """把中文名转成文件安全的 id（拼音不可靠，这里用时间戳+序号兜底）。"""
    s = re.sub(r"[^\w\u4e00-\u9fa5-]+", "_", name.strip()) or "project"
    return s[:48]


def project_dir(project_id: str) -> Path:
    if not _ID_PATTERN.match(project_id):
        raise ValueError(f"非法项目 id：{project_id}")
    return STORAGE_DIR / project_id


def ensure_project(project_id: str) -> Path:
    d = project_dir(project_id)
    if not d.exists():
        raise FileNotFoundError(f"项目不存在：{project_id}")
    return d


def list_projects() -> list[ProjectMeta]:
    metas = []
    for child in sorted(STORAGE_DIR.iterdir()):
        if not child.is_dir():
            continue
        pf = child / PROJECT_FILE
        if not pf.exists():
            continue
        try:
            data = yaml.safe_load(pf.read_text(encoding="utf-8")) or {}
            metas.append(ProjectMeta.model_validate(data))
        except Exception:
            continue
    return metas


def create_project(payload: ProjectCreate) -> ProjectMeta:
    pid = slugify(payload.name)
    # 避免冲突，追加时间戳
    if project_dir(pid).exists():
        pid = f"{pid}_{datetime.now().strftime('%H%M%S')}"
    d = project_dir(pid)
    d.mkdir(parents=True, exist_ok=True)
    meta = ProjectMeta(
        id=pid,
        name=payload.name,
        genre=payload.genre,
        track=payload.track,
        target_episodes=payload.target_episodes,
        purpose=payload.purpose,
        template=payload.template,
        created_at=_now(),
        updated_at=_now(),
    )
    _write_yaml(d / PROJECT_FILE, meta.model_dump())
    _write_yaml(d / CHARACTERS_FILE, {"characters": []})
    _write_yaml(d / OUTLINE_FILE, {"pitch": "", "synopsis": "", "outline": []})
    _write_json(d / SCRIPT_FILE, {"episodes": []})
    (d / VERSIONS_DIR).mkdir(exist_ok=True)
    (d / EXPORTS_DIR).mkdir(exist_ok=True)
    return meta


def get_project(project_id: str) -> ProjectMeta:
    d = ensure_project(project_id)
    data = yaml.safe_load((d / PROJECT_FILE).read_text(encoding="utf-8")) or {}
    return ProjectMeta.model_validate(data)


def update_project(project_id: str, payload: ProjectCreate) -> ProjectMeta:
    meta = get_project(project_id)
    meta.name = payload.name or meta.name
    meta.genre = payload.genre
    meta.track = payload.track
    meta.target_episodes = payload.target_episodes
    meta.purpose = payload.purpose
    meta.template = payload.template
    meta.updated_at = _now()
    _write_yaml(project_dir(project_id) / PROJECT_FILE, meta.model_dump())
    return meta


def delete_project(project_id: str) -> None:
    d = ensure_project(project_id)
    import shutil
    shutil.rmtree(d)


def touch(project_id: str) -> None:
    meta = get_project(project_id)
    meta.updated_at = _now()
    _write_yaml(project_dir(project_id) / PROJECT_FILE, meta.model_dump())


# ---- 通用读写 ----
def read_yaml(project_id: str, filename: str):
    d = ensure_project(project_id)
    p = d / filename
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def write_yaml(project_id: str, filename: str, data) -> None:
    d = ensure_project(project_id)
    _write_yaml(d / filename, data)


def read_json(project_id: str, filename: str):
    import json
    d = ensure_project(project_id)
    p = d / filename
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(project_id: str, filename: str, data) -> None:
    d = ensure_project(project_id)
    _write_json(d / filename, data)


def _write_yaml(path: Path, data) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _write_json(path: Path, data) -> None:
    import json
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
