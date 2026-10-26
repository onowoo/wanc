# -*- coding: utf-8 -*-
"""R13 感情线女主观植入：新增女主林若雪（百草堂掌柜之女，通药理）。
第17集埋线：出场相识 + 身世伏笔（父亲被万春堂逼死、守失传祖传药方）+
半张纸角与秦家医方疑似同源（未来50集埋伏，感情不挑明）。
不破坏主线（残页/王强印章比对仍为主钩子）。保300-500字。"""
import sys

sys.path.insert(0, "E:/project/hongguo/wanc/backend")
from app.services import project_service as ps  # noqa: E402
from app.services import script_parser as parser  # noqa: E402

PID = "演示_神级医仙"

E17 = """第17集 旧案
【内｜秦昭住处｜夜】
赵叔被救回，秦昭替他包扎伤口。
赵叔（哽咽）：少爷，当年你爷爷蒙冤被赶出村……老奴一直记着。
秦昭（手一顿）：蒙冤？爷爷不是……病故的么？
赵叔：是王强他爹，王老财！当年他设局，说你爷爷的医馆用假药害死人，逼得你爷爷净身出户。那医馆就这般被王家夺去！
【动作】秦昭放下绷带，摊开残页。
秦昭：那这枚印章，是……
赵叔（脸色大变）：这、这是王家祖传的章！怎么会在你手上？
秦昭：爷爷临终塞给我的，只让我收好。
赵叔（老泪纵横）：你爷爷不敢说啊！那口冤气，他咽了二十年！
【动作】秦昭点灯，将残页印痕与王强印章并排比对。
【动作】院门叩响，背药篓的姑娘进来——百草堂林若雪，来给老村长送药，瞥见烛下印痕，脚步一顿。
林若雪：这印……万春堂当年，也这么逼我爹。他守着祖传方子不肯交，人就没了。
秦昭：祖传方子？
林若雪（摸出半张纸角）：他临终让我收着，等能辨这方的人，就给看。
【动作】秦昭接过，就着烛火一看，瞳孔微缩。
【本集钩子】：烛火下，两枚印记严丝合缝，分毫不差。秦昭握着那枚旧印，指节收紧，一字一句：王强，你夺我医馆、辱我先人，这笔账——该清了。
"""

if __name__ == "__main__":
    data = ps.read_json(PID, ps.SCRIPT_FILE)
    for ep in data["episodes"]:
        if ep["index"] == 17:
            new_src = E17
            parsed = parser.parse_script(new_src)
            p = parsed[0]
            ep["title"] = p.title
            ep["beats"] = [b.model_dump() for b in p.beats]
            ep["source_text"] = new_src
            ep["hook"] = p.hook
            ep["word_count"] = len(new_src)
    ps.write_json(PID, ps.SCRIPT_FILE, {"episodes": data["episodes"]})
    print("已改第17集：林若雪出场埋感情线+身世/祖传药方伏笔（未来50集埋伏）")
