# -*- coding: utf-8 -*-
"""第七轮内容打磨：改造第15集为脱离冲突线的纯行医温情单元（对白驱动紧凑版）
- 久病村民（瘦汉瘫腿）被慢慢调理治愈——落地"悬壶济世"主题
- 胆小摇摆村民（村民丁怕王强记恨不敢公开夸）——群像差异化
- 环境感官细节（药香混尘土）——降低模板感
结尾保留王强"添把火"钩子（连第16集绑架线）
保持 300-500 字、台词密度≥35%。"""
import sys

sys.path.insert(0, "E:/project/hongguo/wanc/backend")
from app.services import project_service as ps  # noqa: E402
from app.services import script_parser as parser  # noqa: E402

PID = "演示_神级医仙"

E15 = """第15集 济世
【外｜村口广场｜日】
义诊开了半月，村口药香混着尘土。
村民甲：秦大夫的针，比庙里灵。
村民乙：何止，连毒药都能验出来！
李婶（搀着一个瘦小汉子）：秦大夫，我表弟瘫了两年。
瘦汉（苦笑）：大夫，我这腿，怕是废了。
秦昭（搭脉）：脉虚而寒，经络瘀住了。能治。
瘦汉（瞪眼）：能、能治？！
秦昭：头一月能拄拐，三月能走。
瘦汉（红了眼眶）：只要有一分指望，我都认！
秦昭：信我，药连喝三月。
瘦汉（连连点头）：喝！我天天喝！
【动作】此后半月，秦昭隔三日复诊。
【动作】一月后，瘦汉在院里拄拐挪步。
瘦汉（声音发颤）：秦大夫！我能下地了！
李婶（抹泪）：真是菩萨转世！
【动作】义诊收摊，一个缩在墙角的村民凑上来。
村民丁（压低声音）：秦大夫，我不敢在王院长跟前夸您……怕他记恨我。我家那口子的咳嗽，是您治好的。我记着您的大恩。
秦昭（温和地）：治病是分内事，你记不记，我都治。
村民丁（缩回人群）：谢谢秦大夫……
【动作】人群外，王强远远看着。
王强（低声）：好大的名气……我倒要看看能撑几日。
【本集钩子】：王强回到医馆，何掌柜已等在堂上：王院长，你这般坐不住，是该给他添把火了。
"""

if __name__ == "__main__":
    data = ps.read_json(PID, ps.SCRIPT_FILE)
    new_src = E15
    parsed = parser.parse_script(new_src)
    p = parsed[0]
    for ep in data["episodes"]:
        if ep["index"] == 15:
            ep["title"] = p.title
            ep["beats"] = [b.model_dump() for b in p.beats]
            ep["source_text"] = new_src
            ep["hook"] = p.hook
            ep["word_count"] = len(new_src)
    ps.write_json(PID, ps.SCRIPT_FILE, {"episodes": data["episodes"]})
    print("第15集已改造为纯行医温情单元")
