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

add(id="g01", slot="上午", template="卧槽系", claim="assertion",
    text="卧槽！！\n\n太原一栋公寓起火，14 个人没出来\n\n热搜第一是 BLG 赢 T1，第二是大连主帅被泼啤酒\n\n这栋楼上一次消防检查，是谁签的字？",
    **src("太原一建筑火灾"))
add(id="g02", slot="上午", template="不懂就问", claim="assertion",
    text="不懂就问\n\n老人第一次比孩子多\n\n幼儿园会改成老年大学吗？",
    **src("老人数量第一次比孩子多"))
add(id="g03", slot="上午", template="我很好奇", claim="assertion",
    text="我很好奇\n\n光刻机亮的是模型，不是整机\n\n那发布会发布的到底是什么？@grok",
    **src("光刻机模型亮相"))
add(id="g04", slot="上午", template="卧槽系", claim="assertion",
    text="卧槽！！\n\n秦皇岛人说二十年没见过这么大的雪\n\n八达岭长城上已经站满了人\n\n这雪是灾，还是景点？😱😱",
    **src("秦皇岛居民称20年"))
add(id="g05", slot="中午", template="冷知识并置", claim="assertion",
    text="说个冷知识\n\n寒潮预警和大雪，是同一天的事\n\n长城上排队的人\n\n和朋友圈里喊冷的人，大概率是同一批\n\n一个在拍雪，一个在等雪停",
    **src("中央气象台发布大风"))
add(id="g06", slot="中午", template="不懂就问", claim="assertion",
    text="不懂就问\n\nT1 被 BLG 3-1 淘汰，四连冠停在半决赛\n\n那些年说「LPL 打不过 T1」的人\n\n今晚是改口，还是等明年再说？",
    **src("BLG 3-1战胜T1"))
add(id="g07", slot="中午", template="卧槽系", claim="assertion",
    text="卧槽！！\n\n大连英博五年踢到中超冠军，全城免单\n\n那明年保级\n\n店还免单吗？😱",
    **src("大连英博中超夺冠"))
add(id="g08", slot="中午", template="我很好奇", claim="assertion",
    text="我很好奇\n\n胖东来说洗发水不是日本造的，要维权\n\n那之前抢着买的人\n\n图的是「日本」，还是「胖东来」😱",
    **src("卡蓓诺"))
add(id="g09", slot="下午", template="冷知识并置", claim="assertion",
    text="黄渤今年几乎没戏拍，热搜天天有新剧开机。",
    **src("黄渤自曝今年几乎没戏拍"))
add(id="g10", slot="下午", template="卧槽系", claim="assertion",
    text="卧槽！！\n\n实验猴涨到 26 万一只，有养殖场已经没猴可卖\n\n新药排队等猴\n\n以后是我等药，还是猴等我？😱😱",
    **src("实验猴涨至26万"))
add(id="g11", slot="下午", template="不懂就问", claim="assertion",
    text="不懂就问\n\n二十一岁的幼师转行扫街，说待遇好\n\n那是环卫涨了\n\n还是幼师跌了。",
    **src("幼师毕业"))
add(id="g12", slot="下午", template="无模板", claim="assertion",
    text="央视曝光，连夜成立调查组。\n\n这套流程我们看了很多年：镜头来了，人到了；镜头走了，组还在不在。\n\n问题是被查出来的，还是被拍出来的？\n\n下次镜头去了别处，这组散没散。",
    **src("江西赣州成立调查组"))
add(id="g13", slot="下午", template="卧槽系", claim="assertion",
    text="卧槽！！\n\n二十公斤的陨石砸进石家庄的农田\n\n它从哪来没人说得清\n\n今晚肯定有人守在那块地里😱",
    **src("陨石砸进石家庄"))
add(id="g14", slot="傍晚", template="问句开头", claim="assertion",
    text="「汝南」和「驻马店」，是同一个地方吗？\n\n一个名字来自汝水之南\n\n另一个听起来像驿站\n\n中间那一次改名，是谁拍的板？",
    **src("汝南那么好听"))
add(id="g15", slot="傍晚", template="我很好奇", claim="assertion",
    text="我很好奇\n\n把孩子的户口挪去鹤岗，只为高考\n\n三年里\n\n在楼下等雪停的人是谁",
    **src("鹤岗"))
add(id="g16", slot="傍晚", template="我很好奇", claim="assertion",
    text="我很好奇\n\n车企都不想只抱宁德时代一条腿\n\n是腿太贵\n\n还是怕被掐着脖子走",
    **src("宁德时代"))
add(id="g17", slot="晚上", template="无模板", claim="observation",
    text="快递柜免费时长从 24 小时砍到 18 小时，改规则的人很懂我几点下班。")
add(id="g18", slot="晚上", template="无模板", claim="observation",
    text="我妈买了两百斤白菜，够吃到明年春天。")
add(id="g19", slot="晚上", template="问句开头", claim="observation",
    text="电梯里一周换三次广告\n\n住了三年\n\n只记住「整容分期，0 利息」\n\n这算投放成功还是失败。")
add(id="g20", slot="晚上", template="问句开头", claim="observation",
    text="「满 300 减 50」总差 12 块？")

p = pathlib.Path("data/drafts/2026-11-09.jsonl")
p.write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in D) + "\n", encoding="utf-8")

EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]")
BANDS = [(0, 20), (21, 40), (41, 60), (61, 80), (81, 10**9)]
def band(n):
    for i, (lo, hi) in enumerate(BANDS):
        if lo <= n <= hi:
            return i
    return -1
counts = [0] * 5
for d in D:
    t = d["text"]; n = len(t); b = band(n); counts[b] += 1
    print(f'{d["id"]} {n:>3} band{b} lines={sum(1 for l in t.splitlines() if l.strip())}'
          f'{" Q" if "？" in t else "  "}{" E" if EMOJI.search(t) else "  "} {d["template"]}')
print("band counts", counts, "target [3,7,6,2,2]")
