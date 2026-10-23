# -*- coding: utf-8 -*-
"""全局配置：存储路径、模板路径、CORS。"""
from pathlib import Path

# backend/app/config.py -> wanc/
BACKEND_DIR = Path(__file__).resolve().parent.parent      # .../wanc/backend
WANC_ROOT = BACKEND_DIR.parent                           # .../wanc

STORAGE_DIR = WANC_ROOT / "storage"                      # 剧本项目实例根目录
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"  # 提示词 skill 模板

PROJECT_FILE = "project.yaml"
CHARACTERS_FILE = "characters.yaml"
OUTLINE_FILE = "outline.yaml"
SCRIPT_FILE = "script.json"
VERSIONS_DIR = "versions"
EXPORTS_DIR = "exports"

# 前端开发服务器地址（Vite 默认 5173），允许跨域
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def ensure_dirs() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
