# -*- coding: utf-8 -*-
"""后端核心冒烟测试：建项目→加人物→渲染prompt→解析样例→校验→导出。"""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

from app.models.project import ProjectCreate  # noqa: E402
from app.models.character import CharacterPayload  # noqa: E402
from app.services import project_service as ps  # noqa: E402
from app.services import character_service as cs  # noqa: E402
from app.services import prompt_renderer as pr  # noqa: E402
from app.services import script_service as ss  # noqa: E402
from app.services import validator as v  # noqa: E402
from app.services import exporter  # noqa: E402

P = "smoke_demo"


def main():
    # 清理旧项目
    try:
        ps.delete_project(P)
    except Exception:
        pass
    meta = ps.create_project(ProjectCreate(name="重生千金复仇记", genre="女频逆袭",
                                           track="真假千金", target_episodes=40, purpose="submit"))
    P = meta.id
    print("[1] 创建项目:", meta.id, meta.name)

    cs.add_character(P, CharacterPayload(name="苏晚", role_type="protagonist",
                                         core_desire="拿回被抢走的家产，揭露假千金",
                                         core_weakness="前期对过往感情心软",
                                         personality_tags=["冷静隐忍", "智商高", "有仇必报"],
                                         speech_style="短句克制，反击一针见血",
                                         forbidden_behavior=["不会主动撒泼哭闹", "不会无底线原谅背叛者"],
                                         appearance_desc="清冷长相，常穿素色衣裙"))
    cs.add_character(P, CharacterPayload(name="白薇", role_type="antagonist",
                                         core_desire="霸占苏家千金身份",
                                         personality_tags=["贪婪", "势利", "爱算计"],
                                         speech_style="表面柔弱，话里带刺"))
    print("[2] 人物数:", len(cs.list_characters(P)))

    ss.set_outline(P, pitch="被换身的真千金绝地反击，撕碎假千金伪装",
                   synopsis="苏晚被调包十八年，回到苏家却发现所有人都偏袒假千金白薇。苏晚隐忍布局，步步揭穿谎言，夺回家产与尊严。",
                   outline=[{"index": 1, "summary": "真千金被当众羞辱", "node_type": "开局绝境"},
                            {"index": 10, "summary": "第一次中型反转", "node_type": "中型反转"},
                            {"index": 20, "summary": "马甲半暴露", "node_type": "马甲曝光"}])

    rendered = pr.render_prompt(P, "submit_template", "生成前5集完整正文", history_count=0)
    print("[3] 渲染 prompt 长度:", len(rendered["full_prompt"]))
    assert "苏晚" in rendered["full_prompt"] and "禁止行为" in rendered["full_prompt"], "人设注入失败"
    print("[3] 人设快照已注入 prompt：OK")

    # 模拟豆包返回文本
    sample = """第1集 归家
【内｜苏家老宅｜日】
苏晚拖着行李箱，站在金碧辉煌的大门前，眼底一片冷意。
白薇：姐姐，你怎么回来了？
苏晚：这里，也是我的家。
【本集钩子】：苏晚从怀里掏出一份亲子鉴定，正要开口，大门内传来父亲冰冷的命令声。

第2集 风波
【内｜客厅｜日】
苏父：我苏家只有白薇一个女儿。
苏晚：那这份鉴定书，您敢看吗？
【本集钩子】：白薇脸色骤变，死死盯着苏晚手里的文件。
"""
    result = ss.import_text(P, sample, label="冒烟导入")
    print("[4] 导入解析集数:", result["episode_count"], " 校验分:", result["report"]["score"])
    for ep in result["episodes"]:
        print(f"    第{ep['index']}集 钩子={ep['hook']!r} 字数={len(ep['source_text'])}")
    rep = v.validate_episodes(ss.get_episodes(P), cs.list_characters(P))
    print("[5] 校验 issues:", len(rep.issues), " summary:", rep.summary)

    exp = exporter.export_markdown_file(P)
    print("[6] 导出:", exp["filename"])
    print("=== 导出预览（前 600 字）===")
    print(exp["content"][:600])
    print("=== 冒烟测试通过 ===")


if __name__ == "__main__":
    main()
