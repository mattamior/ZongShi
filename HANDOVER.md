# 账号交接：lapplax / @MattDjj → mt.ai

> 交接方：ZongShi 项目（`/Users/jaymini/Code/lab/xcom/ZongShi`，commit `0fbe3ce`）
> 接收方：mt.ai 项目（`/Users/jaymini/Code/lab/mt.ai`）
> 时间：2026-11-06
> 作者：ZongShi 项目代理；账号所有者为 Principal

## 一句话

这个号最初是「复刻 @FKFKFKFKFKTB 发帖风格」的研究副产物，现在已经是 Principal 在用的真号（蓝V、圈子号），要把**发帖、互动、涨粉**的运营交给 mt.ai 现有的 x_send 体系接管。

## 账号现状（2026-11-06 实测）

| 项 | 值 |
|---|---|
| 昵称 | lapplax |
| handle | @MattDjj |
| 数字 ID | 2076195964810113024 |
| bio | share big things for real |
| 注册 | 2026 年 7 月 |
| 数据 | 16 条帖子、34 粉丝、82 关注 |
| 认证 | 蓝V（已开通） |
| 置顶帖 | 「玩 X 没事就想浇个朋友 #交朋友」（浇友风格） |
| Chrome 窗口 | id `1455425140`，单标签页，登录此号 |

**已知异常**：改昵称 / 改 bio 返回 **403**，截至交接时未解决。点赞、关注等写操作正常（已验证）。若 mt.ai 侧要动资料，先复测。

## 目标与边界

- 原目标：复刻对标号 @FKFKFKFKFKTB 的**发帖**风格，为代号 ZongShi 的新号产出规范。研究阶段（P0–P2）已完成。
- 现目标（Principal 2026-11-06）：这个号交给 mt.ai 运营，**涨粉**是首要目的。
- **内容方向已定（Principal 2026-11-06）：时政 / 日常评论**。置顶那条浇友帖是历史，不作为方向。
- 边界：不发色情/政治断言/投资建议；断言必须有来源；任何自动化动作不得激活或干扰 Principal 的其他 Chrome 窗口。

## 已产出的资产（ZongShi 仓库内）

| 路径 | 内容 | 复算命令 |
|---|---|---|
| `data/target/posts-merged/posts.jsonl` | 对标号 **298 条**原创帖，2026-10-20 至 11-06 | `python3 scripts/analyze_posts.py data/target/posts-merged/posts.jsonl` |
| `STYLE.md` | 对标号风格规范（298 条口径） | 同上 |
| `style/target-style.json` | 机器可读规范 | — |
| `style/prompt.md` | 生成用提示词（含配比自检要求） | — |
| `guard/banned.md` | 红线清单与禁用词 | — |
| `guard/check_text.py` | 硬拦截：≤90 字 / ≤6 行 / 单一表情 / 只允许 @grok / 无链接 / 断言须有来源且与标题对得上 | `python3 guard/check_text.py --file <jsonl>` |
| `scripts/fetch_news.py` | 抓当日热榜（头条/知乎/百度），供卧槽系取样 | `python3 scripts/fetch_news.py --output-dir data/news` |
| `scripts/analyze_gap.py` | 样稿与语料的分段/占比对比 | 见脚本头 |
| `scripts/collect_user_timeline.py` | 直连 GraphQL 抓别人时间线（只读） | 见脚本头 |
| `data/drafts/all-posts.md` | 全部 72 条帖子稿（今日 10 条 + 三批样稿） | — |
| `data/drafts/2026-11-06.jsonl` | 今日排期稿 10 条，带 slot/template/来源 | — |
| `scripts/engage.py` | 扫描搜索流 / 点赞 / 关注（后台标签页 DOM 操作） | 见脚本头 |
| `scripts/follow_back.py` | 回关脚本（**已判定策略无效，勿用**） | — |
| `data/growth/pool.jsonl` | 今日扫描的 23 条候选帖 | — |
| `data/growth/ledger.jsonl` | 动作台账（2 条脚本点赞；另有 1 条手工测试点赞未入账） | — |
| `scripts/match_published.py` | 把已发帖子对回稿件，反推排期 | `python3 scripts/match_published.py --window-id <id> --tab 1 --refresh` |
| `data/scheduled/published.jsonl` | 已发布台账：tweet_id / 时刻 / 对应稿件 / 相似度 / 是否被改过 | 同上 |
| `scripts/collect_metrics.py` | 效果回收：每条帖子点赞/回复/转推 + 账号粉丝快照，追加式快照可对比增量 | `python3 scripts/collect_metrics.py --window-id <id> --tab 1 --compare` |
| `data/metrics/snapshots.jsonl` | 每次回收一份快照（账号 + 各帖互动），跨天对比看涨粉 | 同上 |

## 技术事实（踩过的坑，务必先读）

**浏览器操作**

- 只做两件事：`execute (tab N of window W) javascript "..."`，以及用 JS 里的 `location.href` 导航。**禁止** `set URL`、`activate`、`open` —— 都会把窗口提到前台。
- 窗口必须按 `id` 匹配，不能按 index：index 会随窗口增减漂移，按 index 找窗口报过 `-1719 不能获得 "window 26"`。
- 隐藏标签页不会触发 X 的分页（Chrome 节流），**滚动采集无效**；但首屏是服务端渲染的，能直接读 DOM。

**接口**

- `SearchTimeline` / `UserTweetsAndReplies` 对只读账号返回 404；`UserTweets` 可用。
- v1.1 接口（`/i/api/1.1/friends/ids`、`followers/list`、`account/settings`、`users/show`）**全部 404**（code 34）。mt.ai 的 `harvest_following.py` 依赖这套，可能已经坏了，接管前先测。
- GraphQL 需要 `authorization: Bearer` + `x-csrf-token`（从 `ct0` cookie 取），路径前缀 `/i/api/graphql/<queryId>/<Op>`。`UserByScreenName` 可用；`Followers` 返回 422 参数校验失败，未解决。
- 自己账号的 user id 可直接从 `twid` cookie 读（`u%3D<id>`），不需要调接口。

**已验证可行的动作**

- 点赞：在搜索流卡片的 `[data-testid="like"]` 上 `.click()`，按钮变 `unlike` 即成功。已实测 3 次。
- 关注：导航到 `/handle`，点 `primaryColumn` 内的关注按钮（注意排除「订阅/Subscribe」，否则会点成付费订阅）。
- 搜索流首屏约 11–12 条，按 `f=live` 取最新。

## 决策与红线（沿用，不要推翻）

1. 断言必须有来源，且来源标题与正文至少 2 字公共片段（`guard/check_text.py` 会拦）。
2. 正文 ≤90 字、非空行 ≤6 行；表情只用一种、可连打 2–3 个、只在最后一行；只允许 `@grok`；正文不放链接。
3. 不写必须配图才成立的内容。
4. 已废弃：KS 检验（20 条样本下过度敏感）、回关策略（不产生增量）、互关引流帖（mt.ai blocklist 已排除，`出摊|浇友|互关|回关|有关必回|蓝V|涨粉|流量密码`）。
5. 生成后必须跑 `analyze_gap.py` 回查配比：**不加干预时人会自然写得偏短、偏问句、少表情**（实测 21–40 字占 80%，表情 15%）。

## 与 mt.ai 的对接建议

- mt.ai 的 `page_send.py` 已经覆盖关注/点赞/回复，**优先复用**，不要重复实现 `engage.py`。
- 但 mt.ai 的额度是给老号的（关注 289/天）。这个号 34 粉、蓝V 且有过 403，建议 **关注 ≤20/天、点赞 ≤30/天**，间隔 45–120 秒。
- mt.ai 的主体是「回复他人才是增长引擎，关注只是附属动作（25% 概率、延迟 2–5 条）」。这个号目前的主页是浇友风格，**内容定位需要 Principal 拍板**：继续浇友，还是转向时政/AI（`data/drafts` 里的稿子全是后者）。
- 截至交接时已发 4 条：置顶浇友帖（09:20Z）、d01（10:00Z）、d03（10:16Z）、s21（10:31Z，第一批样稿）。
- `data/drafts/2026-11-06.md` 还有 d02、d04–d10 未发。mt.ai 接管后先跑 `match_published.py` 刷新台账再决定发什么，避免重发。

## 未决问题

1. Principal 会**改稿后再发**：已发的 d03 中间插了一句「这是为什么？」，d01、s21 前面补了 `@grok`。台账记录了相似度与 `edited` 标记，归因时按「稿件 + 改动」看，不要把功劳全算给原稿。
2. **效果回收的限制**：`api.fxtwitter.com` 给点赞/回复/转推，但**不返回查看数**；X 网页端也不再在帖子页显示查看数，要看曝光只能开 X 自带的 analytics。
3. **已发帖只看到首屏 4 条**：隐藏标签页不触发翻页；直连 GraphQL `UserTweets` 抓该号只回了 2 条（2026-11-06 实测，原因未查）。台账目前是「首屏可见的帖子」，不是全量。
4. 账号在涨：交接前 34 粉 / 82 关注，两小时后 51 粉 / 89 关注（Principal 手动操作 + 已发帖）。后续看增量用 `collect_metrics.py --compare`。

## 接管第一步（建议顺序）

1. 复测写权限：在 `1455425140` 窗口点一次赞，确认 200/UI 翻转，避免接手后才发现被限。
2. 测 mt.ai 的 `harvest_following.py` 是否还能跑（v1.1 已 404）。
3. 确认内容方向（问 Principal）。
4. 建排期台账：已发/待发/作废，按 `id + 时刻 + 模板` 记录。
5. 24–48 小时后回收首条数据：每条帖的展示、点赞、回复、新增关注。

## 交接验证

```bash
cd /Users/jaymini/Code/lab/xcom/ZongShi
git log --oneline -1                     # 0fbe3ce
python3 guard/check_text.py --file data/drafts/2026-11-06.jsonl   # 检查 10 条，拦截 0 条
wc -l data/target/posts-merged/posts.jsonl                        # 298
```
