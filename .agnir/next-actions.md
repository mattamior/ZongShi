# Next Actions

1. ~~P0 回复路由采集~~ 完成 2026-11-05：`data/target/20261105T1052Z/`，3,223 条本人帖（背景语料）。
2. ~~P1 帖子语料与规范~~ 完成 2026-11-06：`data/target/posts-merged/posts.jsonl` 293 条 + `STYLE.md` + `style/target-style.json` + `style/prompt.md`，由 `scripts/analyze_posts.py` 复算。
3. **P0b 补齐 9-30 至 10-20（阻塞在外部输入）**：需要账号主导出 X 官方档案，只取 `tweets.js` / `tweets-part*.js`。收到后：
   `python3 scripts/import_official_export.py --archive-dir <解压目录>/data --output data/target/official-export/posts.jsonl`
   `python3 scripts/merge_posts.py --output data/target/posts-merged/posts.jsonl data/target/posts-merged/posts.jsonl data/target/official-export/posts.jsonl`
   然后重跑 `analyze_posts.py`，把 STYLE.md 与 target-style.json 的数字整体刷新。导入器已用构造档案验证（回复/转推/@ 开头三类均被正确剔除）。
4. ~~P2 帖子生成与自评~~ 完成 2026-11-06：22 条样稿 `data/eval/20261106T-samples/samples.jsonl`，`guard/check_text.py` 0 拦截，`scripts/analyze_gap.py` 对比 298 条语料，长度分段与四项占比各差 ≤10pp。
5. **每日时事**：`python3 scripts/fetch_news.py --output-dir data/news` 拉头条/知乎/百度热榜到 `data/news/<date>.jsonl`，供卧槽系取样（正文不标来源，出处存 `source_url`）。
6. **接口人设**（`style/new-account.json`）：已完成——昵称 `ZongShi（互～）`、简介 `AI 弄潮儿`，不做固定自称。handle 与头像由 Principal 在开号时手动确定，Agent 不介入。
7. **后置、需单独授权**：P3 发送与节奏、P4 增长闭环。启用前重新评估平台规则风险，并按 `PLAN.md` §5 的"后置"参数表执行。
8. 每次采集/规范变更后做 checkpoint 评估：真变了才更新本文件与 `state.md`，并在 `evidence/` 追加一条可核验记录（时间、命令、结果、覆盖边界）。
