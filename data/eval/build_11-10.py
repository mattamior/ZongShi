#!/usr/bin/env python3
"""生成 2026-11-10 晚场候选：热榜来源 + 双对标参考（@FKFKFKFKFKTB / @btcmos）。

来源取自 data/news/2026-11-10.jsonl（19:00 抓取），只到标题级；
全部人工撰写，正文 ≤90 字、非空行 ≤6、每条挂 @grok。输出 JSONL 与 Markdown。
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
NEWS = ROOT / "data/news/2026-11-10.jsonl"
OUT_JSONL = ROOT / "data/drafts/2026-11-10.jsonl"
OUT_MD = ROOT / "data/drafts/2026-11-10.md"
TAG_NAMES = {"T1": "社会", "T2": "商业", "T4": "民生", "T6": "消费", "T13": "社会",
             "T18": "娱乐", "T21": "科技", "T22": "时政", "T26": "时政", "T29": "生活"}

# (id, slot, topic, template, claim, text, source_title 的匹配片段)
POSTS = [
    ("n001", "19:00", "T13", "跟评", "assertion",
     "南京零元面馆排队排到街口\n\n隔壁一天少卖2000，老板想退租\n\n白吃的人吃爽了，做好人的赚了名声\n\n被挤死那家找谁说理？@grok",
     "零元面馆"),
    ("n002", "19:15", "T13", "站队", "assertion",
     "免费吃面的人越多，隔壁越惨\n\n善意要是没有边界\n\n是不是就等于让老实人买单？\n\n这面馆在救人，还是在抢客？@grok",
     "零元面馆"),
    ("n003", "19:30", "T4", "不懂就问", "assertion",
     "发改委鼓励用人单位办托儿所\n\n那我加班到十点\n\n托儿所几点关门？\n\n最后是老板带娃，还是我带娃上班？@grok",
     "鼓励用人单位办托儿所"),
    ("n004", "19:45", "T4", "跟评", "assertion",
     "照顾老人孩子的压力实实在在\n\n解法是让公司开托儿所\n\n成本不会消失，只会转移\n\n你猜最后从谁工资里扣？@grok",
     "照顾老人孩子压力实实在在"),
    ("n005", "20:00", "T4", "我很好奇", "assertion",
     "幼小初学龄人口已经达峰\n\n以后不是孩子抢学位，是学校抢孩子\n\n那些天价学区房\n\n准备卖给谁？@grok",
     "学龄人口已达峰"),
    ("n006", "20:15", "T21", "跟评", "assertion",
     "国家首次把「失业缓冲期」写进政策\n\n用来接 AI 砸掉的饭碗\n\n缓冲期结束那天\n\nAI 会停下来等你吗？@grok",
     "失业缓冲期"),
    ("n007", "20:30", "T21", "对比", "assertion",
     "AI 抢工作，政策发安全带\n\n可安全带是给车里的人系的\n\n被甩出去的那些\n\n谁管？@grok",
     "失业缓冲期"),
    ("n008", "20:45", "T2", "不懂就问", "assertion",
     "主持人跑了21单，实测抽成13.22%\n\n司机体感全超20%\n\n差的那几个点\n\n藏在哪一单里？@grok",
     "抽成13.22%"),
    ("n009", "21:00", "T2", "跟评", "assertion",
     "2499的指环，戴上就推不倒\n\n被质疑后，企业说要请院士级科学家解释\n\n卖力学就卖力学\n\n拉院士出来干嘛？😅",
     "平衡指环"),
    ("n010", "21:15", "T18", "震惊", "assertion",
     "金鸡奖还没颁，厦门文旅疑似先发了结果又秒删\n\n是手滑\n\n还是名单早就写好了？\n\n那台上哭的笑的，演给谁看？😱",
     "泄露金鸡奖"),
    ("n011", "21:30", "T1", "跟评", "assertion",
     "政务服务中心门头，被挖掘机铲了\n\n嫌疑人已被采取刑事强制措施\n\n一块门头都守不住\n\n里面盖的章守得住吗？@grok",
     "门头遭挖掘机破坏"),
    ("n012", "21:45", "T6", "站队", "assertion",
     "山姆一包泡面卖20，网友吵翻\n\n骂的人未必买，买的人懒得骂\n\n到底面贵\n\n还是逛山姆的人需要它贵？@grok",
     "山姆现20元一包泡面"),
    ("n013", "22:00", "T6", "不懂就问", "assertion",
     "女子称在星巴克坐90分钟，被提醒下单5次\n\n咖啡店卖的是咖啡\n\n还是座位？\n\n不点单的人算顾客还是占座的？@grok",
     "星巴克提醒下单"),
    ("n014", "22:15", "T2", "跟评", "assertion",
     "比亚迪大唐被曝轮毂出厂前后装反\n\n售后说确有部分批次\n\n验车单是谁签的？\n\n下一辆会不会也「部分批次」到我头上？😭",
     "轮毂出厂前后装反"),
    ("n015", "22:30", "T4", "对比", "assertion",
     "猪价创十年新低\n\n菜市场排骨没便宜几块\n\n中间那段谁拿走了？@grok",
     "猪价创10年新低"),
    ("n016", "22:45", "T22", "跟评", "assertion",
     "立陶宛要求「台湾代表处」改名\n\n当初抢着当出头鸟\n\n现在自己往回找补\n\n是扛不住了，还是算完账发现亏了？@grok",
     "台湾代表处"),
    ("n017", "23:00", "T26", "跟评", "assertion",
     "高市早苗去APEC前疯狂加戏\n\n国内支持率不够，就去国际上找镜头\n\n这戏\n\n是演给中国看，还是演给日本选民看？@grok",
     "高市出席APEC"),
    ("n018", "23:15", "T26", "对比", "assertion",
     "伊朗给特朗普下48小时最后通牒\n\n转头特朗普说没必要动武\n\n两边都喊得响\n\n这是要谈，还是各自回去写胜利稿？🤣",
     "48小时最后通牒"),
    ("n019", "23:30", "T26", "跟评", "assertion",
     "俄美乌在阿布扎比谈\n\n欧洲只能在门外等\n\n出钱出武器的没资格上桌\n\n这桌饭最后谁买单？@grok",
     "欧洲三国集团将派联合代表团赴阿布扎比"),
    ("n020", "23:45", "T22", "对比", "assertion",
     "同一天两条热榜\n\n一条说消费新场景活力迸发\n\n一条说供强需弱\n\n到底哪个是真的？@grok",
     "供强需弱"),
    ("n021", "19:00", "T2", "我很好奇", "assertion",
     "胖东来被质疑洗发水产地\n\n一个靠良心出名的地方\n\n最怕的不是贵\n\n是有人发现它也会讲故事\n\n这次信谁？@grok",
     "胖东来"),
    ("n022", "20:00", "T29", "跟评", "assertion",
     "租客退租，连空调外机都搬走了\n\n房东少一台外机\n\n租客多一台外机\n\n这波谁赚了？@grok",
     "空调外机都搬走"),
    ("n023", "21:00", "T29", "不懂就问", "assertion",
     "女儿第一笔工资，全买了自己喜欢的东西\n\n一分没给家里\n\n爸爸上网问怎么看\n\n养孩子是投资，还是养个人？@grok",
     "第一笔工资的用途"),
    ("n024", "22:00", "T21", "跟评", "assertion",
     "华为新折叠电脑，背面加了一块小屏\n\n我盯着想了半天\n\n合上盖我能看啥？\n\n展开后它又在看谁？@grok",
     "鸿蒙折叠电脑"),
    ("n025", "23:00", "T18", "对比", "assertion",
     "中国短剧拿下日本九成市场\n\n他们自己拍不出来\n\n是我们太会爽\n\n还是他们太要脸？🤣",
     "中国短剧占据日本"),
    ("n026", "21:30", "T29", "我很好奇", "assertion",
     "30块中1330万\n\n评论区全在接好运\n\n我就好奇\n\n晒票那位敢不敢把税单也晒出来？😅",
     "30元中了1330万"),
    ("n027", "22:30", "T6", "跟评", "assertion",
     "住酒店掀开被子，上面有干结的粪便\n\n前台第一反应是换房还是免单？\n\n这种卫生\n\n检查表上打几分？@grok",
     "被子上有干结粪便"),
    ("n028", "20:30", "T6", "站队", "assertion",
     "双11第一批被骗的人已经出现\n\n每年提醒，每年有人中\n\n是骗子太快\n\n还是折扣本来就像骗局？@grok",
     "第一批被骗的人"),
    ("n029", "23:30", "T1", "跟评", "assertion",
     "买7块钱早餐，发现卡里26万没了\n\n钱去哪了？\n\n是系统出错\n\n还是有人比银行更懂银行？@grok",
     "卡里近26万没了"),
]


def main() -> None:
    news = [json.loads(l) for l in NEWS.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = []
    missing = []
    for pid, slot, topic, template, claim, text, needle in POSTS:
        src = next((n for n in news if needle in n["title"]), None)
        if src is None:
            missing.append((pid, needle))
            continue
        rows.append({
            "id": pid, "date": "2026-11-10", "slot": slot, "topic": topic,
            "template": template, "claim": claim, "text": text,
            "source_title": src["title"], "source_url": src["url"],
        })
    if missing:
        raise SystemExit(f"来源未匹配：{missing}")

    rows.sort(key=lambda r: (r["slot"], r["id"]))
    OUT_JSONL.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")

    counts = Counter(TAG_NAMES.get(r["topic"], "其他") for r in rows)
    summary = " / ".join(f"{k} {v}" for k, v in counts.most_common())
    lines = [f"# 2026-11-10 晚场候选（{len(rows)} 条）", "",
             f"热点优先：{summary}；来源取自 `data/news/2026-11-10.jsonl`（19:00 抓取），只到标题级。"
             "参考 `data/eval/target-priority.json` 里两个对标账号评分 >4 分的帖子（@FKFKFKFKFKTB / @btcmos）。"
             "全部挂 `@grok`，**未发布、未排期**。", ""]
    for r in rows:
        lines += [f"### {r['id']} {r['slot']}·{r['template']}·{len(r['text'])}字", "", "```", r["text"], "```", ""]
    lines += ["## 来源", ""]
    seen = set()
    for r in rows:
        if r["source_title"] in seen:
            continue
        seen.add(r["source_title"])
        lines.append(f"- {r['source_title']}：{r['source_url']}")
    lines += ["", "## 限制", "",
              "- 热榜只到标题级核实，未打开原文；观察类不引用具体数据。",
              "- 全部人工撰写，未发布，无曝光与互动数据。"]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    over = [(r["id"], len(r["text"])) for r in rows if len(r["text"]) > 90]
    print(f"wrote {OUT_JSONL.relative_to(ROOT)} + {OUT_MD.relative_to(ROOT)} posts={len(rows)}")
    print(f"chars: min={min(len(r['text']) for r in rows)} max={max(len(r['text']) for r in rows)} over90={over}")
    print("slot dist:", Counter(r["slot"] for r in rows).most_common(6))


if __name__ == "__main__":
    main()
