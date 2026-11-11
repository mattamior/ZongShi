#!/usr/bin/env python3
"""2026-11-11 晚场候选：按两号高分帖的「人味」写，不写新闻复述。

来源 data/news/2026-11-11.jsonl（13:40 抓取，三源 73 条）。硬规则照旧：≤90 字、
非空行 ≤6、每条 @grok、争议只提问。输出 JSONL + Markdown。
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
NEWS = ROOT / "data/news/2026-11-11.jsonl"
OUT_JSONL = ROOT / "data/drafts/2026-11-11.jsonl"
OUT_MD = ROOT / "data/drafts/2026-11-11.md"
TAG_NAMES = {"T1": "社会", "T2": "商业", "T4": "民生", "T6": "消费", "T13": "社会",
             "T18": "娱乐", "T21": "科技", "T22": "时政", "T26": "时政", "T29": "生活"}

POSTS = [
    ("q001", "14:00", "T26", "震惊", "assertion",
     "卧槽，罗大佑直接开骂了\n\n「不要脸到家了」\n\n一个唱歌的，把话说得比蓝绿白都清楚\n\n赖清德敢回一句吗？😱",
     "罗大佑炮轰赖清德"),
    ("q002", "14:15", "T18", "跟评", "assertion",
     "前几天还说拍卖冠军车捐给韩红\n\n今天改口，不捐了\n\n捐款这事也能撤回？\n\n是韩红不收，还是自己舍不得？@grok",
     "张雪冠军车拍卖款不再捐"),
    ("q003", "14:30", "T18", "对比", "assertion",
     "梁家辉拿影帝，工作人员伸手要帮他拿奖杯\n\n他摆摆手，自己拎下台\n\n再看某些流量，走两步八个助理\n\n这圈子，真他妈会排面。@grok",
     "梁家辉拒绝工作人员帮拿"),
    ("q004", "14:45", "T4", "站队", "assertion",
     "哈工大硕士卖气球，被骂浪费资源\n\n人家没偷没抢，靠自己吃饭\n\n怎么，学历高就欠社会一个体面？\n\n骂他的人，给他发工资吗？@grok",
     "哈工大硕士卖气球"),
    ("q005", "15:00", "T21", "跟评", "assertion",
     "RTX 5080 直降4000\n\n去年加价抢卡的兄弟，现在还好吗？\n\n等等党赢麻了\n\n下次一涨价，冲得最快的还是你们。🤣",
     "显卡降价"),
    ("q006", "15:15", "T1", "震惊", "assertion",
     "卧槽，卡里26万，6天被分多笔转走\n\n短信提醒被取消，手机还莫名闪烁\n\n这哪是盗刷\n\n这是有人住进她手机里了吧？😱",
     "女子卡里消失了近 26 万元"),
    ("q007", "15:30", "T6", "跟评", "assertion",
     "燃气灶5块钱换电池的事，师傅收260\n\n记者暗访5个师傅，只有2个说实话\n\n剩下3个不是修灶的\n\n是修你智商的吧？@grok",
     "5元换电池"),
    ("q008", "15:45", "T1", "跟评", "assertion",
     "笑死，和平饭店51万的小票是伪造的\n\n警方已介入\n\n炫富炫到要P小票\n\n这届有钱人，连装逼都这么穷？@grok",
     "上海和平饭店6人餐"),
    ("q009", "16:00", "T2", "跟评", "assertion",
     "名校毕业，为泄私愤，匿名举报同事是间谍\n\n一张嘴，差点毁人一辈子\n\n诬告的成本这么低\n\n下次会不会轮到你？@grok",
     "名校毕业生为泄私愤"),
    ("q010", "16:15", "T2", "站队", "assertion",
     "20万朝上的新能源销量，前三全是小米\n\n车评人天天骂，销量天天涨\n\n到底是买车的不懂车\n\n还是车评人不懂人？😅",
     "前三名全是小米"),
    ("q011", "16:30", "T6", "跟评", "assertion",
     "拼多多让商家赔10块，真会做生意\n\n平台定规矩，商家掏钱\n\n10块钱买师傅跑一趟\n\n这算保护消费者，还是拿商家做公关？@grok",
     "拼多多新规"),
    ("q012", "16:45", "T2", "对比", "assertion",
     "比亚迪荷兰办公室被突击搜查\n\n捷豹路虎说方程豹钛7「逆向工程」抄卫士\n\n逆向工程，说得真体面\n\n这词造得，真给面子。@grok",
     "比亚迪荷兰办公室"),
    ("q013", "17:00", "T2", "跟评", "assertion",
     "玛莎拉蒂找尊界合作，车让江淮造\n\n意大利超豪华，贴上中国标\n\n车标是玛莎拉蒂，底盘是江淮\n\n买的人，买的是那个标。@grok",
     "玛莎拉蒂将与尊界合作"),
    ("q014", "17:15", "T26", "跟评", "assertion",
     "空军集训不再发新公文包，旧包消毒再用\n\n过紧日子，先从包开始\n\n下一个\n\n该轮到会议室的水果盘了。@grok",
     "空军某部集训不再新发公文包"),
    ("q015", "17:30", "T1", "站队", "assertion",
     "女士取20万给儿子当彩礼，柜员报警\n\n取自己的钱，先过柜员这关\n\n反诈是好事\n\n反到储户头上，就变味了。@grok",
     "女士取款20万给儿子当彩礼"),
    ("q016", "17:45", "T21", "跟评", "assertion",
     "300块把脸卖了\n\n下一秒，你成了AI短剧里的渣男\n\n合同写没写，这张脸能演多少集？\n\n300块，够买几张电影票？@grok",
     "300元卖掉的脸"),
    ("q017", "18:00", "T1", "对比", "assertion",
     "央视曝光：「取消外卖」的短视频是摆拍\n\n摆拍的人赚流量，信的人骂平台\n\n最后被耍的\n\n永远是信的人。@grok",
     "取消外卖"),
    ("q018", "18:15", "T4", "跟评", "assertion",
     "油价预计下调440元/吨\n\n折合一升大概三毛，加满一箱省十五\n\n涨的时候连夜涨，跌的时候「预计」\n\n省这十五块，够买杯奶茶吗？@grok",
     "油价预计下调440"),
    ("q019", "18:30", "T1", "跟评", "assertion",
     "大家发现没有\n\n夸梁家辉，用的词是「敬业」\n\n不是演技\n\n这行对演员的要求，真低。@grok",
     "梁家辉拒绝工作人员帮拿"),
    ("q020", "18:45", "T4", "不懂就问", "assertion",
     "今年要建10万个护理型养老床位\n\n床位是钢筋水泥\n\n可躺上去的人，谁来翻身？\n\n护工从哪来？@grok",
     "10万个护理型养老床位"),
    ("q021", "19:00", "T21", "跟评", "assertion",
     "董宇辉说 -18℃冷冻保质期变长是常识\n\n常识都值得上热搜\n\n说明什么？\n\n说明我们连常识都要等人教。@grok",
     "董宇辉"),
    ("q022", "19:15", "T6", "跟评", "assertion",
     "缝纫机成了年轻人时尚单品\n\n上一代踩它为了活命\n\n这一代摆它为了拍照\n\n这算复古，还是没苦硬吃？@grok",
     "缝纫机成年轻人时尚单品"),
    ("q024", "19:30", "T1", "站队", "assertion",
     "网红扮成纸人，在景区吓路人小孩\n\n流量有了\n\n被吓哭的孩子，谁来哄？\n\n这不叫创意，叫缺德。😡",
     "纸人"),
    ("q025", "19:45", "T21", "跟评", "assertion",
     "Anthropic 估值下调到1万亿美元，还要募643亿\n\n下调完还有1万亿\n\n这泡沫要是破了\n\n先砸死的是不是写代码的？😱",
     "Anthropic  IPO 估值下调"),

]


def main() -> None:
    news = [json.loads(l) for l in NEWS.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows, missing = [], []
    for pid, slot, topic, template, claim, text, needle in POSTS:
        src = next((n for n in news if needle in n["title"]), None)
        if src is None:
            missing.append((pid, needle))
            continue
        rows.append({"id": pid, "date": "2026-11-11", "slot": slot, "topic": topic,
                     "template": template, "claim": claim, "text": text,
                     "source_title": src["title"], "source_url": src["url"]})
    if missing:
        raise SystemExit(f"来源未匹配：{missing}")

    rows.sort(key=lambda r: (r["slot"], r["id"]))
    OUT_JSONL.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")

    counts = Counter(TAG_NAMES.get(r["topic"], "其他") for r in rows)
    summary = " / ".join(f"{k} {v}" for k, v in counts.most_common())
    lines = [f"# 2026-11-11 晚场候选（{len(rows)} 条）", "",
             f"{summary}；来源 `data/news/2026-11-11.jsonl`（13:40 抓取，只到标题级）。"
             "按两个对标账号 9–10 分帖的语气重写：先给具体细节，再站队、拆台或抛荒诞对比，"
             "不写新闻复述。**未发布、未排期**。", ""]
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
              "- 热榜只到标题级核实，未打开原文；判断句是评论，不是事实断言。",
              "- 全部人工撰写，未发布，无曝光与互动数据。"]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    over = [(r["id"], len(r["text"])) for r in rows if len(r["text"]) > 90]
    print(f"wrote {OUT_JSONL.relative_to(ROOT)} + {OUT_MD.relative_to(ROOT)} posts={len(rows)}")
    print(f"chars min={min(len(r['text']) for r in rows)} max={max(len(r['text']) for r in rows)} over90={over}")


if __name__ == "__main__":
    main()
