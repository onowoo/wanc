# -*- coding: utf-8 -*-
"""剧本校验器：钩子、字数、开篇、敏感词、静态人设 OOC，审稿级一致性规则 + AI 味检测。
静态规则优先，可独立于 LLM 运行；后续可加 LLM 深度 OOC 校验。"""
from __future__ import annotations

import re
from collections import Counter

from ..models.character import Character
from ..models.story import Episode
from ..models.validation import Issue, ValidationReport

MIN_WORDS = 300
MAX_WORDS = 500

SENSITIVE_PATTERNS = [
    "赌博", "高利贷", "裸贷", "涉政", "军警", "宗教", "封建迷信",
    "强买强卖", "虚假医疗", "包治百病", "性别对立", "仇富",
]

OUTDOOR_KEYWORDS = ["村口", "巷口", "广场", "山道", "街道", "长街", "集市", "路口", "门外", "院外",
                    "野外", "山路", "桥头", "井边", "村", "坡", "巷", "街", "田埂", "田间"]
INDOOR_KEYWORDS = ["茶馆", "店内", "店中", "馆", "铺", "堂", "屋", "宅", "府", "楼", "间", "房", "室内"]
NOVEL_NARRATION = ["眼底", "眸色", "眸中", "心头", "心中", "暗暗", "眼神", "目光", "神色",
                   "嘴角", "眉心", "心头一", "心中一动", "眼底掠过", "眸色微动", "心头剧震"]
MIN_LINE_RATIO = 0.35
_SCENE_RE = re.compile(r"【(内|外)｜[^｜】]+｜[日夜晚]】")

AI_REPEAT_WORDS = ["脸色铁青", "攥紧拳头", "冷笑", "眼神", "目光", "脸色骤变", "冷哼一声"]
AI_REPEAT_THRESHOLD = 5
DEUS_PATTERNS = ["恰好", "刚好", "正巧", "凑巧", "恰在此刻", "恰好此时", "说时迟"]
DEUS_THRESHOLD = 3
EAVESDROP_PATTERNS = ["窗外黑影", "黑影一闪", "偷听", "门帘", "一闪而过", "剪影", "隔着窗",
                      "趴窗", "墙根", "站在门外", "恰在门外", "正好听到", "恰巧撞破", "撞破密谋"]
EAVESDROP_THRESHOLD = 4
MAXIM_RE = re.compile(r"[^。，；]{1,9}，[^。；]{1,10}；[^。；]{1,10}，[^。；]{1,8}(是|乃|终归)")
MAXIM_FALLBACK = ["天理难容", "无关输赢", "无关对错", "医者仁心", "大医精诚"]
WRITTEN_WORDS = ["既然", "然而", "倘若", "岂", "莫非", "正如", "方才", "故曰", "勿须", "所料"]
WEAKNESS_GROUNDED_WORDS = ["心软", "念旧", "旧情", "放他一马", "饶他一回", "狠不下心"]
CLIFF_HOOK_WORDS = ["京城", "太医院", "神秘", "主子", "宫里", "宫墙", "御医世家", "来头不小"]
CLIFF_SETUP_WORDS = ["京城", "太医院", "传闻", "御医", "世家", "宫里", "宫里来人", "宫里传话"]
# 第四轮：陷害类桥段同质化——只统计反派"主动设局"词（诬告/诈死/陷害/买凶），
# 不含"设局/构陷"（主角主动设局是加分项、背景讲述与判决词也会误捕）
PLOT_REPEAT_WORDS = ["诬告", "诬陷", "诈死", "陷害", "买凶"]
PLOT_REPEAT_THRESHOLD = 4
# 第四轮：信息白送——反派/杀手/黑衣人主动全盘招供，代替主角主动调查
INFO_GIVEAWAY_PATTERNS = ["全盘招供", "和盘托出", "一五一十", "全都招", "我全说", "都说了",
                          "他全招了", "直接坦白", "如实招来"]
# 第四轮：官府行动触发缺失——官差出动但未交代谁举报/县令是否知晓
# 注："官府"多为背景词（买通官府/惊动官府），非官差实际出动，不列入
GOV_ACTION_WORDS = ["官差", "衙役", "差役", "带走", "锁拿", "抓人"]
GOV_TRIGGER_WORDS = ["县令", "举报", "报案", "状纸", "上堂", "奉县令", "大人", "衙门口",
                     "官府令", "官差来查", "告到"]
# 第五轮：伏笔未回收——反派"找人封口/找证人"埋线后，后续集该证人须出场作证/揭发
# 第六轮扩展：实体线索（藏在地窖/留了底）口头铺垫后，须在后继集转化为实体物证（取回账本/呈堂）
# 回收词聚焦到证人实体（老孙）与具体物证名（黑账）——"呈上/账册"等泛词易被他案公堂呈证误判
FORESHADOW_SETUP_WORDS = ["封口", "闭了嘴", "闭嘴", "藏在地窖", "地窖里", "留了底", "留着底"]
FORESHADOW_RECOVER_WORDS = ["老孙", "老账房", "账房老孙", "黑账"]


def _scene_marks(source: str):
    return _SCENE_RE.finditer(source)


def validate_episodes(episodes, characters=None, target_count=None):
    issues = []
    if not episodes:
        return ValidationReport(issues=[Issue(severity="error", code="no_episodes",
                                              message="没有解析到任何剧集")], score=0)
    characters = characters or []
    score = 100

    repeat_counter = Counter()
    deus_count = 0
    eavesdrop_count = 0
    hook_props = 0
    hook_total = 0
    cliff_hook_hit = False
    cliff_setup_count = 0
    full_body_text = ""
    cliff_ep = None
    plot_eps = set()          # 命中陷害类桥段的集
    giveaway_eps = []          # 命中信息白送的集

    for ep in episodes:
        idx = ep.index
        if not ep.hook and not _has_hook_beat(ep):
            issues.append(Issue(severity="error", code="missing_hook", episode_index=idx,
                                message=f"第{idx}集缺少结尾钩子",
                                suggestion="在结尾增加『【本集钩子】：...』，停在即将揭晓的悬念节点"))
            score -= 8
        wc = ep.word_count
        if wc and wc < MIN_WORDS:
            issues.append(Issue(severity="warning", code="word_count_low", episode_index=idx,
                                message=f"第{idx}集字数 {wc}，低于 {MIN_WORDS}",
                                suggestion="内容偏单薄，补充冲突拉扯细节"))
            score -= 2
        elif wc > MAX_WORDS:
            issues.append(Issue(severity="warning", code="word_count_high", episode_index=idx,
                                message=f"第{idx}集字数 {wc}，高于 {MAX_WORDS}",
                                suggestion="压缩台词与动作，单集控制在 300-500 字"))
            score -= 2
        for pat in SENSITIVE_PATTERNS:
            if pat in ep.source_text:
                issues.append(Issue(severity="error", code="sensitive", episode_index=idx,
                                    message=f"第{idx}集命中敏感词：{pat}",
                                    suggestion="删除/改写相关内容，避免违规下架"))
                score -= 10
        for ch in characters:
            for fb in ch.forbidden_behavior:
                if not fb.strip():
                    continue
                kw = fb.strip().split("，")[0][:6]
                if kw and kw in ep.source_text:
                    issues.append(Issue(severity="warning", code="ooc", episode_index=idx,
                                        message=f"第{idx}集疑似触发『{ch.name}』禁止行为：{fb}",
                                        suggestion="核对是否违背该人物人设红线"))
        for m in _scene_marks(ep.source_text):
            pos = m.group(0)
            if pos.startswith("【内") and any(k in pos for k in OUTDOOR_KEYWORDS) \
                    and not any(i in pos for i in INDOOR_KEYWORDS):
                issues.append(Issue(severity="warning", code="scene_inout", episode_index=idx,
                                    message=f"第{idx}集户外场景误标【内】：{pos}",
                                    suggestion="村口/巷口/广场/山道/街道等室外场景应标【外】"))
                score -= 2
                break
        if ep.word_count:
            line_words = sum(len(b.text) for b in ep.beats if b.kind == "line")
            ratio = line_words / ep.word_count
            if ratio < MIN_LINE_RATIO:
                issues.append(Issue(severity="warning", code="line_density", episode_index=idx,
                                    message=f"第{idx}集台词密度 {ratio:.0%}，低于建议 {MIN_LINE_RATIO:.0%}",
                                    suggestion="动作/叙述偏小说化，增加外部动作与对白拉扯"))
                score -= 2
        novel_hits = [k for k in NOVEL_NARRATION
                      if any(b.kind == "meta" and k in b.text for b in ep.beats)]
        if novel_hits:
            issues.append(Issue(severity="warning", code="novel_narration", episode_index=idx,
                                message=f"第{idx}集含小说化叙述词：{'、'.join(novel_hits[:4])}",
                                suggestion="【动作】里避免心理/眼神/神态描写，改写为可拍外部动作"))
            score -= 2
        if idx in (16, 30) and "赵叔" in ep.source_text and "师叔" in ep.source_text:
            issues.append(Issue(severity="warning", code="redundant_role", episode_index=idx,
                                message="同集出现『赵叔』『师叔』两个功能相似的老伙计，疑似设定冗余",
                                suggestion="合并为一个角色"))
        if target_count is not None and idx == episodes[-1].index and len(episodes) < target_count:
            issues.append(Issue(severity="warning", code="target_mismatch", episode_index=idx,
                                message=f"目标 {target_count} 集，实际仅 {len(episodes)} 集",
                                suggestion="补齐缺失集数，或将目标集数改为实际集数"))

        lines = [b.text for b in ep.beats if b.kind == "line"]
        maxim = [l for l in lines if MAXIM_RE.search(l) or any(m in l for m in MAXIM_FALLBACK)]
        if maxim:
            issues.append(Issue(severity="warning", code="ai_maxim", episode_index=idx,
                                message=f"第{idx}集台词含对仗金句（书面感重）：『{maxim[0][:24]}…』",
                                suggestion="口语化改写，避免开口讲大道理；用短句+行为代替说教"))
            score -= 2
        written = [w for w in WRITTEN_WORDS if any(w in l for l in lines)]
        if written:
            issues.append(Issue(severity="warning", code="ai_written", episode_index=idx,
                                message=f"第{idx}集台词含书面连词：{'、'.join(written[:4])}，偏书面",
                                suggestion="人物口语化：村民土气、反派乡绅圆滑、主角短句克制"))
            score -= 2

        repeat_counter.update(w for w in AI_REPEAT_WORDS if w in ep.source_text)
        deus_count += sum(1 for p in DEUS_PATTERNS if p in ep.source_text)
        eavesdrop_count += sum(1 for p in EAVESDROP_PATTERNS if p in ep.source_text)
        full_body_text += ep.source_text
        cliff_setup_count += sum(1 for p in CLIFF_SETUP_WORDS if p in ep.source_text)
        # 第四轮：桥段同质化 & 信息白送 & 官府行动触发缺失
        if any(p in ep.source_text for p in PLOT_REPEAT_WORDS):
            plot_eps.add(idx)
        if any(p in ep.source_text for p in INFO_GIVEAWAY_PATTERNS):
            giveaway_eps.append(idx)
        has_gov_action = any(w in ep.source_text for w in GOV_ACTION_WORDS)
        has_gov_trigger = any(t in ep.source_text for t in GOV_TRIGGER_WORDS)
        if has_gov_action and not has_gov_trigger:
            issues.append(Issue(severity="warning", code="gov_action_untriggered", episode_index=idx,
                                message=f"第{idx}集官差/官府出动但未交代触发来源（谁举报/县令是否知晓）",
                                suggestion="写明官差因何而来：谁报案/县令批示/正式上堂，禁止无由头天降官差"))
            score -= 2
        if ep.hook:
            hook_total += 1
            if any(k in ep.hook for k in ["印", "章", "信", "黑", "影", "暗格", "残页", "令牌", "密"]):
                hook_props += 1
            if any(k in ep.hook for k in CLIFF_HOOK_WORDS):
                cliff_hook_hit = True
                cliff_ep = idx

    if episodes:
        first = episodes[0]
        head = first.source_text[:120]
        if any(k in head for k in ["小时候", "回忆", "从小", "那年", "从前", "背景介绍", "身世交代"]):
            issues.append(Issue(severity="warning", code="slow_open", episode_index=first.index,
                                message="第1集开头疑似大段背景/回忆铺垫",
                                suggestion="短剧前 8 秒必须直抛绝境冲突"))
            score -= 3

    for w, n in repeat_counter.items():
        if n >= AI_REPEAT_THRESHOLD:
            issues.append(Issue(severity="warning", code="ai_repeat_word",
                                message=f"动作/神态词『{w}』全剧出现 {n} 次，重复率过高",
                                suggestion="差异化神态动作（指尖发抖、嘴角僵住、低头捻扳指沉默），避免一套动作循环"))
            score -= 2
    if deus_count >= DEUS_THRESHOLD:
        issues.append(Issue(severity="warning", code="ai_deus_ex_machina",
                            message=f"全剧出现 {deus_count} 处『恰好/刚好』式机械降神",
                            suggestion="减少贵人恰好救场，改为主角提前布局/自救；贵人只提供事后资源"))
        score -= 2
    if eavesdrop_count >= EAVESDROP_THRESHOLD:
        issues.append(Issue(severity="warning", code="ai_eavesdrop",
                            message=f"全剧出现 {eavesdrop_count} 处窗外黑影/偷听/门帘/门外撞破桥段",
                            suggestion="主角/贵人避免亲自趴窗或恰在门外撞破密谋，改由线人/眼线回报"))
        score -= 2
    if hook_total >= 6 and hook_props / hook_total > 0.6:
        issues.append(Issue(severity="warning", code="ai_hook_single",
                            message=f"物证/悬疑类钩子占比 {hook_props}/{hook_total}，类型单一",
                            suggestion="多用情感钩子（人物秘密、两难选择、心理转折），允许情感落点收尾"))
        score -= 2

    # 第四轮：陷害类桥段同质化——同类"反派下套-主角拆穿"全剧超阈值集
    if len(plot_eps) >= PLOT_REPEAT_THRESHOLD:
        issues.append(Issue(severity="warning", code="ai_repeat_plot",
                            message=f"陷害类冲突（诬告/栽赃/诈死/投毒/买凶/绑架）集中在 {sorted(plot_eps)} 共 {len(plot_eps)} 集，同质化偏高",
                            suggestion="同类冲突全剧最多用 2 次，第四次换手段（篡改卷宗/收买证人/设局反间），避免'反派下套-主角拆穿'模板循环"))
        score -= 2
    # 第四轮：信息白送——关键线索靠反派/杀手主动全盘招供
    if giveaway_eps:
        issues.append(Issue(severity="warning", code="ai_info_giveaway",
                            message=f"第 {'/'.join(map(str, giveaway_eps))} 集关键线索疑似靠反派/杀手主动全盘招供（白送）",
                            suggestion="让反派只吐碎片化线索，主角靠走访/推理/对质拼凑真相，禁止'杀手和盘托出全部阴谋'"))
        score -= 2

    # 第五轮：伏笔未回收——"找人封口"埋线后，后续集该证人须出场作证/揭发
    setup_eps = [ep.index for ep in episodes if any(s in ep.source_text for s in FORESHADOW_SETUP_WORDS)]
    if setup_eps:
        last_setup = max(setup_eps)
        tail = "".join(ep.source_text for ep in episodes if ep.index > last_setup)
        if not any(r in tail for r in FORESHADOW_RECOVER_WORDS):
            issues.append(Issue(severity="warning", code="abandoned_foreshadow",
                                message=f"第 {last_setup} 集埋下『封口/找证人』线索，但后续 {len(episodes) - last_setup} 集未回收（证人未出场/未作证）",
                                suggestion="安排该证人在后续集出场作证/揭发，或直接删除此线，避免废弃伏笔"))
            score -= 2

    # 弱点落地检测仅针对主角：反派弱点（贪财/怕死等）常通过恶行天然体现，无需静态检测；
    # 而"主角弱点标签悬空"是 AI 通病（弱点只写进人物卡、剧情零体现），需强制拦截。
    for ch in characters:
        if ch.role_type != "protagonist":
            continue
        weak = (ch.core_weakness or "").strip()
        if len(weak) > 2 and not any(w in full_body_text for w in WEAKNESS_GROUNDED_WORDS):
            issues.append(Issue(severity="warning", code="weakness_grounded",
                                message=f"『{ch.name}』人设弱点「{weak[:20]}…」全剧无行为落地，标签悬空",
                                suggestion="设计一处该弱点被触发的戏（如对帮凶心软/被旧情羁绊产生犹豫），让弱点真正影响抉择"))
            score -= 2

    if cliff_hook_hit and cliff_setup_count < 2:
        issues.append(Issue(severity="warning", code="cliff_hook_unforeshadowed",
                            episode_index=cliff_ep,
                            message=f"第{cliff_ep}集续集类钩子（京城/太医院/神秘）前文铺垫仅 {cliff_setup_count} 处，过于空降",
                            suggestion="在前 2/3 篇幅零星埋传闻（太医院寻秦氏后人、赵老爷提京城动向），结尾钩子才不生硬"))
        score -= 2

    score = max(0, score)
    if score >= 90:
        summary = "整体质量良好"
    elif score >= 70:
        summary = "存在需修复问题，重点看钩子与字数"
    else:
        summary = "存在较多硬伤，建议按告警逐项修复后再投稿/生成"

    return ValidationReport(issues=issues, score=score, summary=summary)


def _has_hook_beat(ep):
    return any(b.kind == "hook" for b in ep.beats)
