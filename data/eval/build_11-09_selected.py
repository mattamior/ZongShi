import json, pathlib

NEWS = [json.loads(l) for l in open("data/news/2026-11-09.jsonl")]
def src(key):
    for r in NEWS:
        if key in r["title"]:
            return {"source_url": r["url"], "source_title": r["title"]}
    raise SystemExit(f"source not found: {key}")

# 已选：Principal 2026-11-09 从 24 条里挑出的 5 条，正文未改
sel = []
def add(lst, **kw):
    kw.setdefault("date", "2026-11-09")
    lst.append(kw)

add(sel, id="s11", slot="下午", template="时政跟评", claim="assertion", status="selected",
    text="央视一曝光，赣州连夜成立调查组\n\n曝光之前这组人在哪？\n\n@grok", **src("央视曝光后 江西赣州连夜成立调查组"))
add(sel, id="s12", slot="下午", template="社会跟评", claim="assertion", status="selected",
    text="卧槽！！\n\n20 公斤的陨石砸进石家庄农田\n\n一克值多少钱，有懂行的吗？@grok\n\n😱", **src("陨石砸进石家庄"))
add(sel, id="s13", slot="下午", template="社会提问", claim="assertion", status="selected",
    text="大连景区对山东人免费 100 天\n\n本地人进自家门口还得买票\n\n这算好客吗？\n\n@grok", **src("大连多个景区"))
add(sel, id="s15", slot="傍晚", template="体育提问", claim="assertion", status="selected",
    text="张本智和又拿冠军\n\n赢球那两嗓子，你们觉得算庆祝还是没礼貌？\n\n@grok", **src("张本智和"))
add(sel, id="s18", slot="晚上", template="时政提问", claim="assertion", status="selected",
    text="帅化民说台军兵推像在做梦\n\n那这兵推演给谁看？\n\n@grok", **src("帅化民"))

# 备选：按已选 5 条的三种手法（拆穿官方动作 / 奇闻追一个具体数字 / 争议站队）新写
cand = []
add(cand, id="t01", slot="上午", template="人物跟评", claim="assertion", status="candidate",
    text="王健林 14 年后再当万达商管董事长\n\n当年是主动退的，还是不得不退？\n\n@grok", **src("王健林"))
add(cand, id="t02", slot="上午", template="法规跟评", claim="assertion", status="candidate",
    text="破坏秦始皇陵，最高罚一千万\n\n这价码是按哪年的行情定的？\n\n@grok", **src("秦始皇陵"))
add(cand, id="t03", slot="上午", template="奇闻跟评", claim="assertion", status="candidate",
    text="大爷自学网购，一次下单 15 吨红薯\n\n平台就没弹一句「您确定」？\n\n@grok", **src("红薯"))
add(cand, id="t04", slot="中午", template="消费跟评", claim="assertion", status="candidate",
    text="胖东来说赔到破产也要守原则\n\n那赔不起的同行，就不配讲原则了？\n\n@grok", **src("胖东来：哪怕"))
add(cand, id="t05", slot="中午", template="健康跟评", claim="assertion", status="candidate",
    text="医生说普拉提掰不正骨盆\n\n那办卡时说的「矫正」，算谁的？\n\n@grok", **src("普拉提"))
add(cand, id="t06", slot="中午", template="娱乐跟评", claim="assertion", status="candidate",
    text="《持械入宋》主创说没赚 1000 万\n\n那是 999 万还是 1 万？\n\n@grok", **src("持械入宋"))
add(cand, id="t07", slot="下午", template="历史提问", claim="assertion", status="candidate",
    text="汝南改叫驻马店\n\n改名公文里写的理由，怎么没人见过？\n\n@grok", **src("汝南"))
add(cand, id="t08", slot="下午", template="日常跟评", claim="assertion", status="candidate",
    text="今天寒衣节，街上没见几个人烧纸\n\n是规矩变了，还是没人记得了？\n\n@grok", **src("寒衣节"))
add(cand, id="t09", slot="傍晚", template="军事跟评", claim="assertion", status="candidate",
    text="攻击-11 的高清细节一次放出来了\n\n这算给谁看的？\n\n@grok", **src("攻击-11"))
add(cand, id="t10", slot="傍晚", template="电竞提问", claim="assertion", status="candidate",
    text="Bin 被叫「世一上」\n\n今年这表现，这称号配吗？\n\n@grok", **src("Bin 世一上"))
add(cand, id="t11", slot="晚上", template="人物跟评", claim="assertion", status="candidate",
    text="劳动模范董加耕走了\n\n现在的劳模，还有人叫得出名字吗？\n\n@grok", **src("董加耕"))
add(cand, id="t12", slot="晚上", template="产业跟评", claim="assertion", status="candidate",
    text="进博会最火的是运动经济\n\n钱不好赚，运动倒成了生意\n\n这算什么信号？\n\n@grok", **src("进博会"))

for name, rows in (("data/drafts/2026-11-09.jsonl", sel), ("data/drafts/2026-11-09-candidates.jsonl", cand)):
    pathlib.Path(name).write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in rows) + "\n", encoding="utf-8")

for d in sel + cand:
    t = d["text"]
    print(f'{d["id"]} {len(t):>3} L{sum(1 for l in t.splitlines() if l.strip())} {"G" if "@grok" in t else "!"} {d["template"]}')
