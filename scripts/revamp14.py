# -*- coding: utf-8 -*-
"""R13 高优①当众摊牌差异化：第10集结尾改"证物呈衙+官差公示"。
保留当众验毒高光（断肠草掺乌头商陆现形/村民甩药单），但定案/公示环节
交官差按批文对外公布，实现高光差异化（评审点名3/10/22/28任选1处）。
保 300-500 字、台词密度≥35%。"""
import sys

sys.path.insert(0, "E:/project/hongguo/wanc/backend")
from app.services import project_service as ps  # noqa: E402
from app.services import script_parser as parser  # noqa: E402

PID = "演示_神级医仙"

E10 = """第10集 反转
【外｜村口广场｜日】
秦昭当众摆开验药台，一包包药材依次排开。
秦昭：这些，都是从王院长药铺取来的"祖传秘方"。诸位请看。
【动作】取断肠草汁滴入一碗清水，水色瞬间变乌，又投入一只活蛆，蛆虫立时蜷缩而死。
秦昭：断肠草入药能救人，可掺了乌头、商陆，就成了要命的毒。
村民甲（凑近细看）：真死了！这药有毒！
村民乙：王院长卖的就是这？
王强（涨红了脸）：你、你这是栽赃！我药铺里没有这些东西！
【动作】话音未落，一个被救醒的村民冲上来，甩出一张药方。
村民丙：这是我娘在王院长那抓的药单，白纸黑字写着商陆！
【动作】众人围着药单七嘴八舌，王强被挤得连连后退。
秦昭：药是你铺子里出的，单子也是你铺子里开的。这账，赖不掉。
王强（脸色灰败，一甩袖）：一群刁民！我不跟你们一般见识！
【动作】他在唾骂声中仓皇退去。秦昭弯腰收好验药碗，把毒药材与药单单独包成证物。
赵府管家（上前）：秦大夫，这批证物，我连夜呈县衙。县令批了查验，明早官差自会上门公示。
秦昭：有劳管家。
【本集钩子】：王强踉跄回到诊所，哆嗦着从暗格里取出一个木盒，里面静静躺着一枚印章——与秦昭手中残页上的印痕，严丝合缝。
"""

if __name__ == "__main__":
    data = ps.read_json(PID, ps.SCRIPT_FILE)
    for ep in data["episodes"]:
        if ep["index"] == 10:
            new_src = E10
            parsed = parser.parse_script(new_src)
            p = parsed[0]
            ep["title"] = p.title
            ep["beats"] = [b.model_dump() for b in p.beats]
            ep["source_text"] = new_src
            ep["hook"] = p.hook
            ep["word_count"] = len(new_src)
    ps.write_json(PID, ps.SCRIPT_FILE, {"episodes": data["episodes"]})
    print("已改第10集：验毒高光保留，定案/公示环节移交官差按批文对外公布（高光差异化）")
