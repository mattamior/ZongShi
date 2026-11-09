# 2026-11-09 审稿结果落地、晚间候选与审稿站上线

- 时间：2026-11-09 18:00–20:30 (UTC+8)
- 参与：主代理（本机 DSH 会话）；Principal 在审稿站标记、取消分号、指定比例与部署
- 产物：`data/drafts/review.json`、`data/eval/target-ratings.json`、`data/eval/target-priority.json`、`data/drafts/2026-11-09-approved.md`、`data/drafts/2026-11-09-r2.{jsonl,md}`、`data/drafts/2026-11-09-r3.{jsonl,md}`、`site/build_dist.py`、`site/serve.py`（前次提交）、线上 `https://zs.lapplax.com`

## 审稿与评分落地（18:00）

- Principal 在审稿页点「保存到仓库」，`site/serve.py` 直写：`data/drafts/review.json` 430 条 → 已用 57 / 重复 24 / 废弃 349；`data/eval/target-ratings.json` 298 条 → 0 分 8、1 分 35、4 分 194、5 分 21、6 分 3、7 分 7、8 分 11、9 分 9、10 分 10。
- 重跑 `scripts/style_priority.py data/eval/target-ratings.json`：scored 298、kept(>4) 61。
- 修正画像口径：此前 `profile` 把对标账号 4 条 300+ 字爆料长文算进长度基准，p90 虚高到 256 字；改为只统计 ≤90 字帖（`profile_n` 26），p90 = 68、中位 46、问句 42%、带图 42%。README 同步。

## 取消分号（18:36）

- Principal：「不用分什么号A号B，我自己挑」。
- `site/template.html` 删账号筛选与卡片徽标，`site/build_site.py` 不再输出 `account`；新候选不带该字段；旧批次 JSONL 字段保留但不被读取。
- decisions / state / README / `2026-11-09-batch.md` 表头同步为单号口径。

## 候选补充

- r2：24 条，18:00–23:45，按已采纳 57 条的手法（中位 37.5 字、92% 落在 21–40 字）。
- r3：100 条，11-09 19:00 → 11-10 19:45，社会 25 / 时政 11 / 民生 44 = 80%（Principal 要求 >70%）；其余消费 6、科技 4、产业 4、娱乐 3、体育 3。
- 来源：`data/news/2026-11-09.jsonl`（18:55 快照）+ `2026-11-09-1804.jsonl`；早间 11:25 快照备份为 `2026-11-09-morning.jsonl`（原文件被 18:04 抓取覆盖）。

## 审稿站上线

- `site/build_dist.py` 打包 `site/dist`（`index.html`、`target.html`、`style.css`、`img/`、`_headers` 的 `X-Robots-Tag: noindex`、`robots.txt`）。
- Cloudflare Pages 项目 `zongshi-review`（生产分支 `main`），首次部署 114 文件 7.7 MB；Principal 自行绑定 `zs.lapplax.com`，约 10 分钟后证书生效（绑定瞬间 522）。
- 非 `localhost` 主机名时页面隐藏「保存到仓库」（`POST /save` 只由 `site/serve.py` 提供）。

## 命令与结果

```
python3 guard/check_text.py --file data/drafts/2026-11-09-r2.jsonl   # 24 条，拦截 0
python3 guard/check_text.py --file data/drafts/2026-11-09-r3.jsonl   # 100 条，拦截 0
python3 scripts/style_priority.py data/eval/target-ratings.json      # scored=298 kept(>4)=61
python3 site/build_site.py                                           # 554 条 / 5 个日期
python3 site/build_dist.py                                           # 114 文件 7.7 MB
npx wrangler@4 pages deploy site/dist --project-name zongshi-review  # 成功
curl https://zs.lapplax.com/ | sha256sum                             # 与 site/index.html 一致
```

## 覆盖边界与未验证项

- 热榜条目只到标题级核实，未打开原文；观察类候选不引来源、不做事实断言。
- 线上审稿站：手机端布局未实测；线上标注状态的「导出 → 回传仓库」闭环未跑通；`X-Robots-Tag` 只防索引，URL 仍公开。
- 未发布、未排期、未登录账号、未操作 mt.ai。
