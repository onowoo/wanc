# -*- coding: utf-8 -*-
"""版本快照与 diff：每次导入/重大修改自动存版本，支持列表、对比、回滚。"""
from __future__ import annotations

import difflib
import json
from datetime import datetime

from . import project_service as ps


def snapshot(project_id: str, label: str = "快照") -> str:
    """把当前 script.json + outline.yaml 复制到 versions/<ts>/ 下。返回版本标识。"""
    d = ps.ensure_project(project_id)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    vdir = d / ps.VERSIONS_DIR / ts
    vdir.mkdir(parents=True, exist_ok=True)
    script_data = ps.read_json(project_id, ps.SCRIPT_FILE)
    outline_data = ps.read_yaml(project_id, ps.OUTLINE_FILE)
    (vdir / "script.json").write_text(
        json.dumps(script_data, ensure_ascii=False, indent=2), encoding="utf-8")
    (vdir / "outline.yaml").write_text(
        _dump_yaml(outline_data), encoding="utf-8")
    (vdir / "meta.json").write_text(
        json.dumps({"label": label, "time": ts}, ensure_ascii=False, indent=2), encoding="utf-8")
    return ts


def list_versions(project_id: str) -> list[dict]:
    d = ps.ensure_project(project_id)
    vdir = d / ps.VERSIONS_DIR
    items = []
    for child in sorted(vdir.iterdir(), reverse=True):
        if child.is_dir():
            items.append({"version": child.name, "label": _version_label(child)})
    return items


def _version_label(vdir) -> str:
    meta = vdir / "meta.json"
    if meta.exists():
        try:
            return json.loads(meta.read_text(encoding="utf-8")).get("label", "")
        except Exception:
            return ""
    return ""


def restore(project_id: str, version: str) -> dict:
    d = ps.ensure_project(project_id)
    vdir = d / ps.VERSIONS_DIR / version
    if not vdir.exists():
        raise FileNotFoundError(f"版本不存在：{version}")
    # 先快照当前状态，再回滚
    snapshot(project_id, f"回滚前备份")
    script_data = json.loads((vdir / "script.json").read_text(encoding="utf-8"))
    outline_data = _load_yaml(vdir / "outline.yaml")
    ps.write_json(project_id, ps.SCRIPT_FILE, script_data)
    ps.write_yaml(project_id, ps.OUTLINE_FILE, outline_data)
    ps.touch(project_id)
    return {"restored": version, "episode_count": len(script_data.get("episodes", []))}


def diff(project_id: str, version_a: str, version_b: str) -> list[str]:
    """两个版本的分集正文文本行级 diff。"""
    a = _episode_lines(project_id, version_a)
    b = _episode_lines(project_id, version_b)
    return list(difflib.unified_diff(a, b, fromfile=version_a, tofile=version_b, lineterm=""))


def _episode_lines(project_id: str, version: str) -> list[str]:
    d = ps.ensure_project(project_id)
    p = d / ps.VERSIONS_DIR / version / "script.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    lines = []
    for ep in data.get("episodes", []):
        lines.append(f"===== 第{ep.get('index', '?')}集 {ep.get('title', '')} =====")
        lines.extend((ep.get("source_text", "") or "").splitlines())
    return lines


def _dump_yaml(data) -> str:
    import yaml
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def _load_yaml(path):
    import yaml
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
