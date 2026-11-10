# ZongShi — X 账号风格研究与内容工作台

本仓库研究 X 账号 [@FKFKFKFKFKTB](https://x.com/FKFKFKFKFKTB)（高水水（互～））的**发帖**风格，产出可复算的规范、生成提示词与稿件，并保留真实账号的发布匹配、互动和指标回收工具。回复语料只作背景，不进入发帖规范。

## 当前状态（2026-11-07 同步）

- 研究主线 P0–P2 已完成：可取得的原创帖语料共 **298 条**，覆盖 2026-10-20 至 11-06；已产出规范与自评样稿。账号更早的原创帖未取得，已停止追补，不宣称覆盖全部历史。
- 已有真实账号的内容与台账：2026-11-06 交接记录中的昵称为 **lapplax**、handle 为 **@MattDjj**；原计划 `ZongShi（互～） / AI 弄潮儿` 已作废。账号资料、指标及接口可用性均为历史快照，本次未在线复测。
- 目标是将该号的发帖、互动与增长交由 **mt.ai** 接管；内容方向已定为**时政 / 日常评论**，增长为首要目的。
- **交接尚未完成，周一（2026-11-09）继续**（用户 2026-11-07 确认）。接管说明见 [HANDOVER.md](HANDOVER.md)。现有脚本和历史动作记录不能视为接管已完成或当前自动化正在运行。

## 当前产物

| 产物 | 用途 |
|---|---|
| [STYLE.md](STYLE.md)、[style/target-style.json](style/target-style.json) | 298 条原创帖的风格结论、机器可读规则与指标 |
| [style/prompt.md](style/prompt.md) | 帖子生成提示词与配比自检要求 |
| [style/new-account.json](style/new-account.json) | 账号接口资料、已作废的人设方案与身份边界 |
| [data/target/posts-merged/posts.jsonl](data/target/posts-merged/posts.jsonl) | 去重后的 298 条原创帖；同目录保留 `post-stats.json` |
| [data/target/20261105T-posts/](data/target/20261105T-posts/)、[data/target/20261105T1052Z/](data/target/20261105T1052Z/)、[data/target/timeline-api/](data/target/timeline-api/) | 镜像与登录态时间线采集留档；均有覆盖边界 |
| [data/eval/](data/eval/)、[guard/banned.md](guard/banned.md)、[guard/check_text.py](guard/check_text.py) | 三批样稿、自评报告与出稿前硬拦截 |
| [data/drafts/](data/drafts/) | 稿件库；每条用「`### id 时段·模板·字数` + 代码块」排版，便于整条复制；稿件日期不证明已排期或已发布 |
| [scripts/fetch_news.py](scripts/fetch_news.py) | 手动获取当日热榜，为时事稿保留来源 |
| [scripts/match_published.py](scripts/match_published.py)、[data/scheduled/published.jsonl](data/scheduled/published.jsonl) | 已发帖与稿件匹配；现有台账仅覆盖当时首屏可见的 4 条 |
| [scripts/collect_metrics.py](scripts/collect_metrics.py)、[data/metrics/snapshots.jsonl](data/metrics/snapshots.jsonl) | 帖子互动与账号指标历史快照；查看数可能缺失 |
| [scripts/engage.py](scripts/engage.py)、[data/growth/](data/growth/) | 已有搜索扫描、点赞、关注工具和历史台账；回关工具 `follow_back.py` 已废弃，勿用 |
| [site/](site/) | 审稿站：`index.html` 审全部历史稿件（四态标记、标签出处、配图、顶部图表、导入导出），`target.html` 给对标账号 298 条帖子打 0–10 分 |
| [HANDOVER.md](HANDOVER.md) | mt.ai 接管说明、历史技术限制与未决问题 |
| [PLAN.md](PLAN.md) | 当前进度摘要与早期方案；历史回复策略、配额不作为当前执行参数 |

## 本地复核

以下命令只做本地统计与文本检查，不触达账号；检查通过不代表事实已核实或发布效果已验证。

```bash
python3 scripts/analyze_posts.py data/target/posts-merged/posts.jsonl
python3 guard/check_text.py --file data/drafts/2026-11-07_08.jsonl
```

批量出稿后另用 `scripts/analyze_gap.py` 对照语料检查分布，调用方式见脚本头。

## 审稿页（site/）

```bash
python3 site/fetch_images.py               # 抓新闻配图（原文 og:image 优先，取不到用图片搜索兜底）
python3 site/build_target.py               # 生成对标账号评分页 site/target.html（298 条，0–10 分）
python3 site/plan_dedupe.py                # 按正文去重：逐字或几乎一样的帖子只留一条，其余标记「重复」
python3 site/build_site.py                 # 读 data/drafts/*.jsonl，生成 site/index.html（数据内嵌）
python3 site/serve.py 8777                  # 静态服务 + GET/POST /api/state + POST /save（直接写仓库文件）
# 打开 http://127.0.0.1:8777/index.html
python3 site/build_dist.py                 # 打包 site/dist（页面 + 样式 + 配图 + noindex 头 + _worker.js）
npx wrangler pages deploy site/dist --project-name zongshi-review
# 线上 https://zs.lapplax.com（自定义域）＝ https://zongshi-review.pages.dev（Pages 项目 zongshi-review，生产分支 main）
```

- 顶部导航在「稿池 / 对标评分」之间切换；工具栏单行、图表独立成行不吸顶，卡片区与图表同宽（1180px）。
- 覆盖 `data/drafts/*.jsonl` 里所有日期，可用「全部日期」筛选；顶部四张图是按状态/日期/题材/字数统计，标完即时更新。
- 四颗按钮对应四种结论：**复制 = 合格（自动标记已用）**、**重复 = 与已发内容撞车**、**废弃 = 不合格**、**编辑 = 优化（就地改完保存）**。
- 每张卡显示编号、时段、来源（选定/备选/池）、题材、类型、问句/陈述、字数，以及出处标题和原文链接；稿件不分账号（2026-11-09 起取消号 A/号 B 分配）。
- 单条想指定配图：在 `data/drafts/image_overrides.json` 里加 `"<id>": {"q": "搜索关键词", "credit": "百度图片"}`（也可用 `url` 钉死），再跑 `fetch_images.py`。
- 配图是新闻图：先取原文 `og:image`，取不到用图片搜索兜底，仍没有就不配图（日常观察类本来没有）。图片放正文右侧、点击看大图，图下标注「原文 / 百度图片（非原文配图）」；**「复制图片」与正文「复制」是两颗独立按钮**。
- 状态（已用/废弃/改动/配图）存在浏览器 localStorage；点「保存到仓库」直接把 `data/drafts/review.json` 写进仓库（需要 `site/serve.py`），也可「导出」下载。
- 页面排版与图表对齐 mt.ai 看板：顶栏 + 状态徽章、KPI 数字卡（带占比进度条）、四张带坐标轴的图表（状态环图 / 按日期 / 题材排行 / 字数分布）、吸顶工具栏、两栏稿件列表；评分页同款。图表是自绘 SVG，不引图表库。
- 状态（已用/废弃/重复/改动/配图/评分）**双向同步**：页面启动先 `GET /api/state` 拉线上状态，之后每次标记都会 `POST /api/state` 写回（800ms 防抖）。线上由 `site/worker.js`（部署成 `_worker.js`）+ KV `ZS_STATE` 承载；本地 `site/serve.py` 提供同形状接口，直接读写仓库文件。localStorage 只是离线缓存。
- 仓库 ↔ 线上用 `scripts/sync_state.py`：`pull` 把线上状态并回 `data/drafts/review.json` 与 `data/eval/target-ratings.json`（保留原有顺序，只追加新 id）；`push` 把仓库状态推到线上（`--replace` 整段覆盖）。`show` 只看线上摘要。
- `build_dist.py` 仍会把仓库状态注入页面（`window.__ZS_SEED__`）作为离线兜底：接口不可用时按仓库状态渲染。线上带 `X-Robots-Tag: noindex`，但知道 URL 的人仍可打开；`/api/state` 无鉴权，最坏情况是被改写标记，可用 `push --replace` 从仓库恢复。
- 快捷键：`j`/`k` 切换、`c` 复制、`d` 重复、`x` 废弃、`e` 编辑。
- 顶部「隐藏重复」默认勾选：`plan_dedupe.py` 把正文逐字/近似重复的帖子（优先留选定、备选，其次按时间）预置为「重复」并隐藏；同主题换角度的帖子不算重复。取消勾选或把状态筛成「重复」才看得到。
- 必须用 http 打开：`file://` 下浏览器不给剪贴板权限，复制会失败。

## 对标账号评分（site/target.html）

- 298 条原创帖逐条打 0–10 分，状态存 `localStorage: zs-target-ratings`，可导出 `target-ratings.json`。
- 没耐心逐条打时点「按展示补分」：只补未评分的，>10000 展示记 5 分、1000–10000 记 4 分、≤1000 记 1 分；已评的不动。也可以把导出文件给我，跑 `python3 scripts/fill_ratings.py <导出.json>` 服务端合并（结果 `data/eval/target-ratings-filled.json`）。
- 点「保存到仓库」会把 `data/eval/target-ratings.json` 直接写进仓库（需要 `site/serve.py`）；也可导出后手动放。拿到后，跑 `python3 scripts/style_priority.py data/eval/target-ratings.json`，生成 `data/eval/target-priority.json`：按分数排序的正文 + 高分帖的长度/行数/问句/带图画像。
- **起草只参考评分 >4 分的帖子**：`python3 scripts/style_priority.py data/eval/target-ratings.json` 默认按 `--min 4` 过滤，输出里的 `ranking` 就是可参考清单；`profile` 用作长度和句式基准，只统计 ≤90 字的帖子（对标账号少数 300+ 字爆料长文不进基准，`profile_n` 是计入条数）。

## 已定边界

- 借用表达结构，不复制对标账号的具体事件和断言；争议内容须有公开来源，无来源不写事实断言。
- 原创正文 ≤90 字、非空行 ≤6 行；不写依赖配图才成立的内容；来源保存在稿件元数据中。
- 长文复盘体裁继续延后；不编造学历、战绩、机构或个人经历，不做固定自称。
- 选题不由简介推导；内容方向沿用已定的时政 / 日常评论。
- 本仓库未建设完整自动发送闭环，接管优先复用 mt.ai；继续运营前核对账号、授权、写权限与台账，避免重发。文档同步不启动发布、互动或资料修改。

## Agnir Project Instructions

本项目的规范激活与操作说明位于 [AGNIR.md](AGNIR.md)。本节仅作为向后兼容的定位入口。
