import json, pathlib

NEWS = [json.loads(l) for l in open("data/news/2026-11-09.jsonl")]
def src(key):
    for r in NEWS:
        if key in r["title"]:
            return {"source_url": r["url"], "source_title": r["title"]}
    raise SystemExit(f"source not found: {key}")

C = []
def add(**kw):
    kw.setdefault("date", "2026-11-09"); kw.setdefault("status", "candidate")
    C.append(kw)

# 保留：Principal 未否掉的四条
add(id="t01", slot="上午", template="人物跟评", claim="assertion",
    text="王健林 14 年后再当万达商管董事长\n\n当年是主动退的，还是不得不退？\n\n@grok", **src("王健林"))
add(id="t02", slot="上午", template="法规跟评", claim="assertion",
    text="破坏秦始皇陵，最高罚一千万\n\n这价码是按哪年的行情定的？\n\n@grok", **src("秦始皇陵"))
add(id="t03", slot="上午", template="奇闻跟评", claim="assertion",
    text="大爷自学网购，一次下单 15 吨红薯\n\n平台就没弹一句「您确定」？\n\n@grok", **src("红薯"))
add(id="t06", slot="中午", template="娱乐跟评", claim="assertion",
    text="《持械入宋》主创说没赚 1000 万\n\n那是 999 万还是 1 万？\n\n@grok", **src("持械入宋"))
add(id="t12", slot="晚上", template="产业跟评", claim="assertion",
    text="进博会最火的是运动经济\n\n钱不好赚，运动倒成了生意\n\n这算什么信号？\n\n@grok", **src("进博会"))

# Principal 亲自改过的稿，逐字保留
add(id="t07", slot="下午", template="历史提问", claim="assertion",
    text="汝南改叫驻马店\n\n是谁tm排板的\n\n改名公文里写的理由，怎么没人见过？\n\n@grok", **src("汝南"))

# 新写：按「骂到具体动作」的路子替换被否的六条
add(id="u01", slot="上午", template="油价跟评", claim="assertion",
    text="油价又要下调了\n\n涨三块的时候没这么大动静\n\n降两毛就上热搜？\n\n@grok", **src("油价"))
add(id="u02", slot="中午", template="娱乐跟评", claim="assertion",
    text="蔡少芬一家五口住 83 平，说很知足\n\n这面积搁内地算刚需吧？\n\n@grok", **src("蔡少芬"))
add(id="u03", slot="中午", template="人口跟评", claim="assertion",
    text="老人比孩子多了\n\n催生的和催退休的，是同一批人吧？\n\n@grok", **src("老人数量"))
add(id="u04", slot="下午", template="医疗跟评", claim="assertion",
    text="实验猴 26 万一只\n\n药还没影，猴先成了硬通货\n\n谁在囤？\n\n@grok", **src("实验猴"))
add(id="u05", slot="下午", template="科技跟评", claim="assertion",
    text="光刻机重大突破\n\n点开一看又是个模型\n\n真机是造不出来，还是不能给人看？\n\n@grok", **src("光刻机"))
add(id="u06", slot="下午", template="消费跟评", claim="assertion",
    text="胖东来那瓶洗发水，当初吹日本原产\n\n现在否认，说要维权\n\n那先道歉的该是谁？\n\n@grok", **src("卡蓓诺"))
add(id="u07", slot="傍晚", template="时政跟评", claim="assertion",
    text="对美加税又暂停 24%\n\n这税到底是打美国人的，还是给我们交的？\n\n@grok", **src("24%"))

add(id="v01", slot="上午", template="热搜跟评", claim="assertion",
    text="太原那栋楼，14 个人没出来\n\n通报说原因正在查\n\n查完是不是又一句「举一反三」？\n\n@grok", **src("太原"))
add(id="v02", slot="中午", template="职场跟评", claim="assertion",
    text="试用期没转正，离职员工改了后台，公司赔几百万\n\n权限给了六个月才想起收？\n\n@grok", **src("试用期"))
add(id="v03", slot="下午", template="体育提问", claim="assertion",
    text="普通人拼命能 20 分钟跑完 5 公里？\n\n说能的，明早六点操场见\n\n@grok", **src("5公里"))
add(id="v04", slot="晚上", template="科技跟评", claim="assertion",
    text="英伟达 7600 万的货失踪了\n\n芯片还能长腿跑？\n\n@grok", **src("英伟达"))

pathlib.Path("data/drafts/2026-11-09-candidates.jsonl").write_text(
    "\n".join(json.dumps(d, ensure_ascii=False) for d in C) + "\n", encoding="utf-8")
for d in C:
    t = d["text"]
    print(f'{d["id"]} {len(t):>3} L{sum(1 for l in t.splitlines() if l.strip())} {"G" if "@grok" in t else "!"} {d["template"]}')
