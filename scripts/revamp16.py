# -*- coding: utf-8 -*-
"""R13c 评审低优·林若雪加戏：第22集医道大会辨识方子。
呼应第17集药方伏笔（"和我爹那味家传方，路子一样"）+巩固盟友人设+感情含蓄（不挑明）。
保300-500字、台词密度≥35%。"""
import sys

sys.path.insert(0, "E:/project/hongguo/wanc/backend")
from app.services import project_service as ps  # noqa: E402
from app.services import script_parser as parser  # noqa: E402

PID = "演示_神级医仙"

E22 = """第22集 辩医
【内｜县城·医道大会｜日】
县城三年一度的医道大会开锣，各地名医齐聚，比诊辨药，一决高下。
钱师爷（高声）：今番大会，请诸位就"乌头之毒当如何解"各陈其方。
【动作】众医纷纷落笔，唯有秦昭静坐不动。
医者甲：乌头之毒，当以甘草、生姜缓之！
医者乙：非也，当用绿豆甘草汤催吐！
【动作】秦昭等众人说尽，才缓缓开口。
秦昭：乌头劫阴，首当固本培元。甘草绿豆，只解皮毛，救不了心阳将绝之人。当以附子、干姜回阳，佐以童便引毒下行。
【动作】满场一静，主审老医师猛地站起。
老医师：高论！这才是医家正途！敢问小友师承？
秦昭：家传而已。
【动作】台下角落，一个背药篓的姑娘也直起身——百草堂林若雪。
林若雪（低声自语）：附子回阳、童便引毒……和我爹那味家传方，路子一样。
秦昭（转头）：林姑娘也懂？
林若雪（抿唇，别过脸）：我不懂医道，只是听得顺耳。先生莫笑。
【动作】老医师提笔，把秦昭的方子列为本届之最。
【动作】台下，何掌柜脸色铁青，王强的脸已扭曲。
【本集钩子】：大会散场，钱师爷快步凑到王强耳边：不能再等了。明日，就让那出"人命大戏"，上台。
"""

if __name__ == "__main__":
    data = ps.read_json(PID, ps.SCRIPT_FILE)
    for ep in data["episodes"]:
        if ep["index"] == 22:
            new_src = E22
            parsed = parser.parse_script(new_src)
            p = parsed[0]
            ep["title"] = p.title
            ep["beats"] = [b.model_dump() for b in p.beats]
            ep["source_text"] = new_src
            ep["hook"] = p.hook
            ep["word_count"] = len(new_src)
    ps.write_json(PID, ps.SCRIPT_FILE, {"episodes": data["episodes"]})
    print("已改第22集：林若雪医道大会辨识方子，呼应药方伏笔+巩固盟友（感情含蓄不挑明）")
