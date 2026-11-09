import json, pathlib, re

NEWS = [json.loads(l) for l in open("data/news/2026-11-09.jsonl")]
def src(key):
    for r in NEWS:
        if key in r["title"]:
            return {"source_url": r["url"], "source_title": r["title"]}
    raise SystemExit(f"source not found: {key}")

D = []
def add(**kw):
    kw.setdefault("date", "2026-11-09")
    D.append(kw)

add(id="s01", slot="上午", template="热搜跟评", claim="assertion",
    text="太原那场火，走了 14 个人\n\n通报说还在查原因\n\n你家楼道那堆纸箱，谁管？@grok", **src("太原一建筑火灾"))
add(id="s02", slot="上午", template="社会提问", claim="assertion",
    text="老人正式比孩子多了\n\n四个老人，一个娃\n\n以后是谁养谁？@grok", **src("老人数量第一次比孩子多"))
add(id="s03", slot="上午", template="科技跟评", claim="assertion",
    text="光刻机重大突破，又上热搜了\n\n仔细一看，亮相的是模型，不是整机\n\n真机什么时候能跑起来？@grok", **src("光刻机模型亮相"))
add(id="s04", slot="上午", template="热搜跟评", claim="assertion",
    text="秦皇岛人说二十年没见过这么大的雪\n\n雪还没化，八达岭先挤满了人\n\n看雪还是看人？@grok", **src("秦皇岛居民称20年"))
add(id="s05", slot="中午", template="体育跟评", claim="assertion",
    text="BLG 3-1 把 T1 送走，四连冠没了\n\n赛前说「LPL 打不过 T1」的，出来走两步？@grok", **src("BLG 3-1战胜T1"))
add(id="s06", slot="中午", template="卧槽系", claim="assertion",
    text="卧槽！！\n\n大连英博夺冠，全城免单\n\n明年保级还免吗？@grok\n\n😱😱", **src("大连英博中超夺冠"))
add(id="s07", slot="中午", template="消费跟评", claim="assertion",
    text="胖东来那瓶洗发水，当初说是日本产的\n\n现在又说不是，要维权\n\n买的人到底图哪个？@grok", **src("卡蓓诺"))
add(id="s08", slot="中午", template="娱乐跟评", claim="assertion",
    text="黄渤说自己今年几乎没戏拍\n\n可热搜上天天有新剧开机\n\n是戏少了，还是他贵了？@grok", **src("黄渤自曝今年几乎没戏拍"))
add(id="s09", slot="下午", template="产业跟评", claim="assertion",
    text="实验猴 26 万一只，养殖场没猴可卖\n\n新药排队等猴\n\n以后是人等药，还是药等人？@grok\n\n😱", **src("实验猴涨至26万"))
add(id="s10", slot="下午", template="就业提问", claim="assertion",
    text="21 岁幼师转行扫街，说待遇好\n\n是环卫涨了，还是幼师撑不住了？@grok", **src("幼师毕业"))
add(id="s11", slot="下午", template="时政跟评", claim="assertion",
    text="央视一曝光，赣州连夜成立调查组\n\n曝光之前，这组人在干嘛？@grok", **src("江西赣州成立调查组"))
add(id="s12", slot="下午", template="社会跟评", claim="assertion",
    text="20 公斤的陨石砸进石家庄农田\n\n这玩意一克值多少钱，有懂的吗？@grok\n\n😱", **src("陨石砸进石家庄"))
add(id="s13", slot="下午", template="社会提问", claim="assertion",
    text="大连景区对山东人免费 100 天\n\n本地人进自家门口景区还得买票\n\n这是好客还是生意？@grok\n\n😱", **src("大连多个景区"))
add(id="s14", slot="傍晚", template="时政跟评", claim="assertion",
    text="对美加税又暂停 24%\n\n暂停到什么时候？这笔账谁算？@grok", **src("中方继续暂停"))
add(id="s15", slot="傍晚", template="体育提问", claim="assertion",
    text="张本智和又拿冠军了\n\n赢球吼那两嗓子，算不算没礼貌？\n\n你们怎么看？@grok", **src("张本智和"))
add(id="s16", slot="傍晚", template="体育跟评", claim="assertion",
    text="里夫斯砍 43 分，湖人五连胜\n\n詹姆斯不在，湖人反而更顺\n\n这是巧合吗？@grok", **src("里夫斯"))
add(id="s17", slot="傍晚", template="热搜跟评", claim="assertion",
    text="大连主帅被泼了一身啤酒，滑倒还光速变脸\n\n赢了球泼啤酒，输了球泼什么？@grok", **src("大连主帅被泼啤酒"))
add(id="s18", slot="晚上", template="时政提问", claim="assertion",
    text="帅化民说台军兵推像在做梦\n\n那这兵推是演给谁看的？@grok", **src("帅化民"))
add(id="s19", slot="晚上", template="日常跟评", claim="observation",
    text="「满 300 减 50」\n\n最后永远差 12 块\n\n这 12 块是算法故意留的吗？@grok")
add(id="s20", slot="晚上", template="日常跟评", claim="observation",
    text="快递柜免费时长从 24 小时砍到 18 小时\n\n改规则的人，很懂我几点下班？@grok")

p = pathlib.Path("data/drafts/2026-11-09.jsonl")
p.write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in D) + "\n", encoding="utf-8")

EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]")
BANDS = [(0, 20), (21, 40), (41, 60), (61, 80), (81, 10**9)]
cnt = [0]*5
for d in D:
    t = d["text"]; n = len(t)
    b = next(i for i,(lo,hi) in enumerate(BANDS) if lo <= n <= hi); cnt[b] += 1
    has_grok = "@grok" in t
    print(f'{d["id"]} {n:>3} b{b} L{sum(1 for l in t.splitlines() if l.strip())} '
          f'{"G" if has_grok else "!"}{" E" if EMOJI.search(t) else "  "} {d["template"]}')
print("bands", cnt)
print("missing @grok:", [d["id"] for d in D if "@grok" not in d["text"]])
