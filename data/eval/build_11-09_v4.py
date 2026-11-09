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
    text="太原那场火，14 个人没出来\n\n通报说原因还在查\n\n我家楼道也堆着纸箱，谁管？\n\n@grok", **src("太原一建筑火灾"))
add(id="s02", slot="上午", template="社会提问", claim="assertion",
    text="老人比孩子多了\n\n四个老人一个娃\n\n以后这娃是养老还是上班？\n\n@grok", **src("老人数量第一次比孩子多"))
add(id="s03", slot="上午", template="科技跟评", claim="assertion",
    text="光刻机又重大突破了\n\n热搜点进去一看，亮的是个模型\n\n真机能跑了吗？\n\n@grok", **src("光刻机模型亮相"))
add(id="s04", slot="上午", template="热搜跟评", claim="assertion",
    text="秦皇岛二十年没见过这么大的雪\n\n长城上人比雪厚\n\n你们那儿下雪还有人往上爬吗？\n\n@grok", **src("秦皇岛居民称20年"))
add(id="s05", slot="中午", template="体育跟评", claim="assertion",
    text="BLG 3-1 把 T1 送走了\n\n四连冠没了\n\n赛前说「LPL 永远打不过 T1」的呢\n\n出来走两步？@grok", **src("BLG 3-1战胜T1"))
add(id="s06", slot="中午", template="卧槽系", claim="assertion",
    text="卧槽！！\n\n大连英博夺冠，全城免单\n\n明年保级还免吗？@grok\n\n😱😱", **src("大连英博中超夺冠"))
add(id="s07", slot="中午", template="消费跟评", claim="assertion",
    text="胖东来那洗发水，卖的时候说日本造\n\n现在否认造假，要维权\n\n当初抢的人，图它日本还是图胖东来？@grok", **src("卡蓓诺"))
add(id="s08", slot="中午", template="娱乐跟评", claim="assertion",
    text="黄渤说自己今年几乎没戏拍\n\n热搜上天天有新剧开机\n\n是戏少，还是他贵？\n\n@grok", **src("黄渤自曝今年几乎没戏拍"))
add(id="s09", slot="下午", template="卧槽系", claim="assertion",
    text="卧槽！！\n\n实验猴 26 万一只，养殖场没猴可卖\n\n新药排队等猴\n\n这是要人等药，还是药等人？@grok\n\n😱", **src("实验猴涨至26万"))
add(id="s10", slot="下午", template="就业提问", claim="assertion",
    text="21 岁幼师转行扫街，说待遇好\n\n评论区说说，是环卫涨了还是幼师撑不住？@grok", **src("幼师毕业"))
add(id="s11", slot="下午", template="时政跟评", claim="assertion",
    text="央视一曝光，赣州连夜成立调查组\n\n曝光之前这组人在哪？\n\n@grok", **src("江西赣州成立调查组"))
add(id="s12", slot="下午", template="社会跟评", claim="assertion",
    text="卧槽！！\n\n20 公斤的陨石砸进石家庄农田\n\n一克值多少钱，有懂行的吗？@grok\n\n😱", **src("陨石砸进石家庄"))
add(id="s13", slot="下午", template="社会提问", claim="assertion",
    text="大连景区对山东人免费 100 天\n\n本地人进自家门口还得买票\n\n这算好客吗？\n\n@grok", **src("大连多个景区"))
add(id="s14", slot="傍晚", template="时政跟评", claim="assertion",
    text="对美加税又暂停 24%\n\n暂停到哪天，这账谁算？\n\n@grok", **src("中方继续暂停"))
add(id="s15", slot="傍晚", template="体育提问", claim="assertion",
    text="张本智和又拿冠军\n\n赢球那两嗓子，你们觉得算庆祝还是没礼貌？\n\n@grok", **src("张本智和"))
add(id="s16", slot="傍晚", template="体育跟评", claim="assertion",
    text="里夫斯 43 分，湖人五连胜\n\n这波连胜到底谁带的？\n\n@grok", **src("里夫斯"))
add(id="s17", slot="傍晚", template="热搜跟评", claim="assertion",
    text="大连主帅被泼一身啤酒，滑倒还光速变脸\n\n赢球泼啤酒，输球泼啥？\n\n@grok", **src("大连主帅被泼啤酒"))
add(id="s18", slot="晚上", template="时政提问", claim="assertion",
    text="帅化民说台军兵推像在做梦\n\n那这兵推演给谁看？\n\n@grok", **src("帅化民"))
add(id="s19", slot="晚上", template="日常跟评", claim="observation",
    text="「满 300 减 50」\n\n永远差 12 块\n\n这 12 块是算法留的吗？\n\n@grok")
add(id="s20", slot="晚上", template="日常跟评", claim="observation",
    text="快递柜免费时长从 24 小时砍到 18 小时\n\n改规则的人很懂我几点下班\n\n@grok")

add(id="s21", slot="晚上", template="冷知识并置", claim="assertion",
    text="大连英博夺冠，全城免单\n\n大连 GDP 完成「逆袭之战」\n\n一个城市一天两条热搜，都叫逆袭\n\n@grok", **src("大连GDP"))
add(id="s22", slot="晚上", template="数字名单", claim="assertion",
    text="24%：对美加税又暂停\n\n26 万：一只实验猴\n\n14 人：太原那场火\n\n300 万：宿舍里手搓的 AI 漫剧\n\n这组数字什么水平？@grok", **src("中方继续暂停"))
add(id="s23", slot="晚上", template="AI 跟评", claim="assertion",
    text="大三男生在宿舍手搓 AI 漫剧，一年营收 300 万\n\n评论区已经开始卖课了吧？\n\n@grok", **src("大三男生宿舍手搓"))
add(id="s24", slot="晚上", template="产业跟评", claim="assertion",
    text="进博会最火的是运动经济\n\n钱不好赚，运动装备反而卖爆\n\n这算降级还是升级？\n\n@grok", **src("进博会"))

p = pathlib.Path("data/drafts/2026-11-09.jsonl")
p.write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in D) + "\n", encoding="utf-8")

EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]")
for d in D:
    t = d["text"]
    print(f'{d["id"]} {len(t):>3} L{sum(1 for l in t.splitlines() if l.strip())} '
          f'{"G" if "@grok" in t else "!"}{" E" if EMOJI.search(t) else "  "} '
          f'{"?" if "？" in t else " "} {d["template"]}')
