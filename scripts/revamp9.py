# -*- coding: utf-8 -*-
"""第1集重写为「重生·先知引擎」爆款开篇（压缩版）：
睁眼爷爷还活着(命运包袱0:30秒) → 先知知杀局(金手指显形) → 反灌毒药(爽点碾压)
→ 济世堂姓秦(包袱) → 官差封馆(钩子=上一世的杀招重现)
目标：六项开篇爆点要素全命中（开篇爆点诊断 6/6），300-500 字、台词密度≥35%。"""
import sys

sys.path.insert(0, "E:/project/hongguo/wanc/backend")
from app.services import project_service as ps  # noqa: E402
from app.services import script_parser as parser  # noqa: E402

PID = "演示_神级医仙"

E1 = """第1集 重生
【内｜济世堂后屋｜日】
秦昭猛地睁眼，冷汗浸透。爷爷在榻上，气若游丝。
秦昭（攥紧爷爷的手，眼眶发红）：爷爷，您还在……这一次，我不会让您再死一回。
爷爷（虚弱）：昭儿……医馆，怕是守不住了。
秦昭：守得住。爷爷，上一世，就是今夜，王强灌您断肠草，含冤而死。
爷爷（震惊）：你、你怎么知道？
秦昭：我死过一回了。这辈子，我要把您的医馆和命，都保下来。
【内｜济世堂堂屋｜夜】
入夜，王强端着"补药"登门。
王强（满脸和善）：秦老爷子，我熬了副补药，趁热喝吧。
秦昭（挡在爷爷身前，盯着王强袖口）：王强，你袖子里那包，才是要命的。
王强（脸色一僵）：秦大夫，这话从何说起？
秦昭：断肠草。上一世你用它毒死我爷爷，这一世，我要你当场现形。
【动作】王强要强灌，秦昭反手夺碗灌回。
秦昭：既是好药，你先尝。
王强（掐着喉咙干呕，跪倒）：你、你……
【动作】秦昭摸出爷爷的残页。
秦昭：济世堂，姓秦。这一世，你一样抢不走。
【本集钩子】：门外响起官差的声音：奉县令之命，济世堂卖假药害人，即刻封馆！
"""

if __name__ == "__main__":
    data = ps.read_json(PID, ps.SCRIPT_FILE)
    new_src = E1
    parsed = parser.parse_script(new_src)
    p = parsed[0]
    for ep in data["episodes"]:
        if ep["index"] == 1:
            ep["title"] = p.title
            ep["beats"] = [b.model_dump() for b in p.beats]
            ep["source_text"] = new_src
            ep["hook"] = p.hook
            ep["word_count"] = len(new_src)
    ps.write_json(PID, ps.SCRIPT_FILE, {"episodes": data["episodes"]})
    print("第1集已重写为重生·先知引擎爆款开篇")
