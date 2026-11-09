#!/usr/bin/env python3
"""11-09 晚间轮（18:00–23:45）24 条候选：只按对标评分 >4 分的帖子取手法。

    python3 data/eval/build_11-09_r2.py

来源标题与链接从 data/news/2026-11-09.jsonl 按关键词回填，不手写 URL。
输出 data/drafts/2026-11-09-r2.{jsonl,md}；日期标签不证明已排期或已发布。
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
NEWS = ROOT / "data/news/2026-11-09.jsonl"
OUT_JSONL = ROOT / "data/drafts/2026-11-09-r2.jsonl"
OUT_MD = ROOT / "data/drafts/2026-11-09-r2.md"

# (id, slot, topic, template, text, 来源标题关键词)
ROWS = [
    ("r01", "18:00", "T9", "不懂就问",
     "无锡女厕上了站立小便位\n排队的根因，是姿势不对？\n\n@grok",
     "无锡出现"),
    ("r02", "18:15", "T30", "跟评",
     "写「画地为牢」被辞，理由是工作不积极\n那不发朋友圈算不算消极？\n\n@grok",
     "画地为牢"),
    ("r03", "18:30", "T26", "跟评",
     "黄仁勋承认婚外情\n中方回应「女方为中国工作」\n\n美国老板的家事，怎么成了外交问题？\n\n@grok",
     "黄仁勋婚外情"),
    ("r04", "18:45", "T22", "跟评",
     "外媒说中国有 60 万枚英伟达芯片\n是数出来的，还是编出来的？\n\n@grok",
     "60万枚英伟达"),
    ("r05", "19:00", "T26", "震惊体",
     "特朗普说，没他就没有以色列\n\n建国那会儿，他在哪？@grok\n\n😱😱",
     "没我以色列"),
    ("r06", "19:15", "T26", "跟评",
     "菲外交部公开敲打自家防长\n涉华的话，外交部先不认了\n\n@grok",
     "菲外交部"),
    ("r07", "19:30", "T24", "不懂就问",
     "攻击-11 实弹首发命中\n「首发」两个字\n之前是没打，还是没中？\n\n@grok",
     "攻击-11实弹"),
    ("r08", "19:45", "T26", "跟评",
     "石破茂被自民党党内警告\n日本首相换得比季节还快\n这警告是罚他还是保他？\n\n@grok",
     "石破茂等4人"),
    ("r09", "20:00", "T26", "不懂就问",
     "伊朗说摧毁了霍尔木兹的敌方导航系统\n「敌方」是谁，一字没提\n\n@grok",
     "霍尔木兹"),
    ("r10", "20:15", "T26", "跟评",
     "内塔尼亚胡要第三次当总理\n仗打成这样，位置还在\n这国家没别人了？\n\n@grok",
     "内塔尼亚胡"),
    ("r11", "20:30", "T1", "跟评",
     "「顺其自然」又捐 111 万\n二十多年没人知道是谁\n\n@grok",
     "顺其自然"),
    ("r12", "20:45", "T17", "冷知识并置",
     "99 人的群，98 个是托\n剩下那个就是客户\n这也能骗到人？@grok\n\n🤣🤣",
     "99人的群"),
    ("r13", "21:00", "T4", "跟评",
     "哈工大研究生卖气球，月入三千，说不后悔\n是气球太赚，还是专业太坑？\n\n@grok",
     "哈工大研究生"),
    ("r14", "21:15", "T1", "跟评",
     "吃完结账反悔，开车把同桌的人碾死\n就为一顿饭钱\n\n@grok",
     "碾死同餐者"),
    ("r15", "21:30", "T6", "不懂就问",
     "比亚迪大唐，前后轮毂装反\n出厂检测是盖章用的？\n\n@grok",
     "轮毂装反"),
    ("r16", "21:45", "T6", "不懂就问",
     "小电驴也卖不动了\n是没钱了，还是没必要了？\n\n@grok",
     "小电驴"),
    ("r17", "22:00", "T3", "跟评",
     "进博会氢能摩托签了 3000 万出口单\n国内路上见过一辆吗？\n\n@grok",
     "氢能摩托车"),
    ("r18", "22:15", "T3", "跟评",
     "五家车企不约而同少用宁德时代\n商量过？\n被谁吓到了？\n\n@grok",
     "宁德时代的单一合作"),
    ("r19", "22:30", "T3", "跟评",
     "马斯克说软银在违约燃气轮机订单\n卖车的替发电行业爆料\n账单哪来的？\n\n@grok",
     "软银正在违约"),
    ("r20", "22:45", "T21", "我很好奇",
     "微信又更新 8 个功能\n没一个是我要的\n你们想要的那个，敢说？@grok\n\n😭😭",
     "微信8大新功能"),
    ("r21", "23:00", "T21", "跟评",
     "张朝阳说 AI 漫剧像化肥催的西红柿\n是化肥催的，还是人写的？\n\n@grok",
     "张朝阳说从来不看AI漫剧"),
    ("r22", "23:15", "T10", "跟评",
     "梁家辉一个人拉箱子坐高铁领奖\n小明星出门带八个保镖\n谁更像演员？\n\n@grok",
     "梁家辉"),
    ("r23", "23:30", "T5", "跟评",
     "王楚钦说要重新审视自己\n输一场就审视\n赢的时候怎么不审视？\n\n@grok",
     "王楚钦发文"),
    ("r24", "23:45", "T11", "跟评",
     "米兰车展，中国机车的展车零件被偷光\n主办方安保是摆设？\n\n@grok",
     "张雪机车"),
]


def load_news() -> list[dict]:
    return [json.loads(line) for line in NEWS.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    news = load_news()
    rows = []
    for pid, slot, topic, template, text, keyword in ROWS:
        hit = next((n for n in news if keyword in n["title"]), None)
        if hit is None:
            raise SystemExit(f"{pid}: 热榜里找不到来源 {keyword!r}")
        rows.append({
            "id": pid, "date": "2026-11-09", "slot": slot, "topic": topic,
            "template": template, "claim": "assertion", "text": text,
            "source_url": hit["url"], "source_title": hit["title"],
            "variant": "1",
        })

    OUT_JSONL.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")

    lines = ["# 2026-11-09 晚间轮（24 条）", "",
             "按对标评分 >4 分帖的手法写（`data/eval/target-priority.json` 的 ranking），"
             "全部挂 `@grok`；热榜来自 `data/news/2026-11-09.jsonl`（18:04 抓取）。**未发布、未排期**。",
             ""]
    for r in rows:
        chars = len(r["text"])
        lines += [f"### {r['id']} {r['slot']}·{r['template']}·{chars}字", "", "```", r["text"], "```", ""]
    lines += ["## 来源", ""]
    lines += [f"- {r['id']}：{r['source_title']}" for r in rows]
    lines += ["", "## 限制", "",
              "- 热榜条目只到标题级核实，未打开原文；正文未出现标题以外的数字与人名。",
              "- 全部人工撰写，未发布，无曝光与互动数据。", ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_JSONL.relative_to(ROOT)} ({len(rows)} 条), {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
