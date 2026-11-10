# 2026-11-10 新增对标账号 @btcmos

- 时间：2026-11-10 18:37–18:45 (UTC+8)
- 触发：Principal「新增一个对标账号 https://x.com/btcmos」

## 账号快照（FxTwitter `/2/profile`，2026-11-10）

- handle `btcmos`，显示名「香港老雷」，数字 ID `1865722200185307136`。
- 61,793 粉丝 / 28,943 关注 / 9,027 条状态；2024-12-08 注册；蓝 V（individual）。
- 简介：`美股老韭｜BTC玩家｜加密合约｜AI资讯|AI投资｜数据整理｜WEIBO：香港老雷`。
- 与主对标 @FKFKFKFKFKTB（时政 / 八卦 / 日常短帖）不同，该号偏美股、BTC、合约与 AI，属于内容方向互补的第二个参考样本。

## 采集

- `scripts/collect_target.py` 泛化出 `--handle` / `--account-id` / `--profile-ref` / `--since`：默认仍是原账号，新增账号不必再改常量；`--since` 到达下界即停止翻页并把窗口外行剔除。
- 命令：`python3 scripts/collect_target.py --handle btcmos --account-id 1865722200185307136 --output-dir data/target/btcmos-20261110 --since 2026-10-20 --with-replies 0`。
- 结果：30 页 / 569 行 / 564 条唯一状态；本人 560 条（原创 514 / 回复 46 / 转推 0），重复行 5，窗口外丢弃 4 条；时间窗 **2026-10-20 → 2026-11-10**（22 个日期）。
- `termination_reason=since_reached`，`api_cursor_exhausted=false`：**不是全量历史**，只覆盖窗口；对账号报告的 9,027 条状态，观察比 6.2%。
- 落盘：`data/target/btcmos-20261110/originals.jsonl`（514 条，评分页语料）、`authored.jsonl`、`replies.jsonl`、`reposts.jsonl`、`source/pages/page-0001..0030.json`、`source/progress.json`、`collection.json`。
- 采集脚本补了一处收尾写入：结束原因与页数现在同时落到 `progress.json`，与 `collection.json` 一致。

## 页面与脚本

- 新增 `data/target/accounts.json` 作为账号清单（key / handle / 显示名 / 原创帖文件 / 颜色 / 窗口 / 备注）；`site/build_target.py` 按清单合并语料，当前 **812 条**（298 + 514）。
- `site/target.html`：顶部账号页签「全部 / 高水水（互～） / 香港老雷」，KPI、评分分布与进度环、筛选、按展示补分都跟随当前账号；每张卡加账号徽章（颜色区分）。评分仍是全局 `{id: score}`，localStorage 键 `zs-target-ratings` 与线上 `/api/state` 形状不变，原有 298 条评分不受影响。
- `scripts/style_priority.py`：读 `accounts.json`，按账号分别统计画像与清单，输出 `accounts.<key>.{profile,ranking}`；顶层 `profile` / `ranking` 保留为合并口径，旧用法不破。

## 验证

- 无头 Chrome + CDP（1440 / 390 宽，本地 `serve.py`）：
  - 初始 812 条卡片、页签计数 812 / 298 / 514；点「香港老雷」后总数 514、已评 0、未评 514、可见卡片 514、元信息切到「香港老雷 · 514 条」。
  - 给一条打 7 分后已评 1、均分 7.0，服务端收到写入（测试条目已从 `target-ratings.json` 移除，文件回到 298 条且无 diff）。
  - 「未评分 / 9–10 / 7–8 / 5–6 / 0–4」筛选与「按展示补分」确认框按当前账号范围工作；390 宽下 `scrollWidth == innerWidth`，无横向溢出。
- `python3 site/build_target.py` 通过；`python3 scripts/style_priority.py data/eval/target-ratings.json` 输出 `fkfk=61 / btcmos=0`。
- 手机截图 `target-btcmos-mobile.png`、桌面 `target-btcmos-desktop.png` / `target-btcmos-cards.png` 由子代理做视觉复核。

## 部署与线上验证

- `python3 site/build_dist.py` 后 `npx wrangler pages deploy site/dist --project-name zongshi-review --branch main` 部署成功（deployment `36fc615c.zongshi-review.pages.dev`）。
- 线上 `https://zs.lapplax.com/target.html` 实测：页签 812 / 298 / 514，默认已评 298（来自 KV），点「香港老雷」后总数 514、已评 0、可见 514 张卡，同步徽章「已同步 18:47:43」；`/api/state` 正常返回。
- 手机截图（390 宽、本地加载宽度）修掉一处旧问题：评分页图表区的内联 `grid-template-columns` 压住了 680px 单列规则，手机上「评分分布」被挤成约 85px 宽；改为 `.charts.charts2` 类后单列，重测 `scrollWidth == innerWidth`、图表 366px 宽。

## 补分口径改为 1–10（同日）

- Principal 指出「既然是 1–10 分就按规则用满，10 分是上限」。原 2026-11-09 的 5 分上限作废，改为：≥100 万→10、50–100 万→9、20–50 万→8、10–20 万→7、5–10 万→6、1–5 万→5、1000–1 万→4、100–1000→3、10–100→2、<10→1；已评的不动。
- 页面「按展示补分」确认框按档位列条数；`scripts/fill_ratings.py` 改为读 `accounts.json` 双账号、支持 `--account` / `--out`，同规则。
- 用现有 298 条评分试跑：btcmos 514 条将补成 10×5 / 9×8 / 8×25 / 7×25 / 6×55 / 5×213 / 4×180 / 3×3；未写入仓库或线上，等 Principal 在页面点。
- 页面确认框实跑（本地 serve.py + CDP，confirm 返回 false）：档位行数与上述一致，取消后已评仍 0，未写入；`viewScore` 边界值 10/100/1000/10000/100000/1000000 均验证。规则改动后重新部署（`5388b053.zongshi-review.pages.dev`），线上 HTML 已含 `VIEW_RULE`。

## 覆盖边界与未决

- @btcmos 现有评分 **0 条**：未评分前不进入 `>4 分` 起草参考，`target-priority.json` 里 `accounts.btcmos` 为空。要参与起草，先在评分页打分或按展示补分，再重跑 `style_priority.py`。
- 窗口为 10-20 起，账号更早历史未采集（账号报告 9,027 条状态）；第三方镜像不保证完整，缺失/删除/设限帖可能不在。不做全历史翻页，避免评分页继续膨胀。
