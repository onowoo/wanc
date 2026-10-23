# -*- coding: utf-8 -*-
"""FastAPI 应用入口。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import ALLOWED_ORIGINS, ensure_dirs
from .routers import projects, characters, prompts, scripts, exports

ensure_dirs()

app = FastAPI(
    title="wanc 剧本工程化工具",
    version="0.1.0",
    description="红果短剧剧本生产、人设管理、校验与导出后端",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(characters.router)
app.include_router(prompts.router)
app.include_router(scripts.router)
app.include_router(exports.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "wanc"}
