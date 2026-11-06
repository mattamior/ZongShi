# Current State

- Project: 复刻 X 账号 `@FKFKFKFKFKTB`（高水水（互～），数字 ID `2105258399885844480`）的**发帖**风格，为一个尚未创建的新号（代号 ZongShi）产出可复算的规范与提示词。**学习对象是帖子，不是回复**（Principal 2026-11-06 修正）。
- Authorized Project Entry Point: this repository root (`/Users/jaymini/Code/lab/xcom/ZongShi`).
- Agnir Core/profile: `1.0` / `repository-filesystem/1.0`; primary lineage: `urn:zongshi:lineage:primary`; distribution `v1.0.2` from revision `b5626394ec40a5cb7a28c01892acde07cc0adc8e`.
- **Phase: research only (Principal, 2026-11-05).** 采集、分析、规范、自评；不接账号、不发布。发送段（`send.py` / `record_sent.py` / `metrics.py` / `candidates/` / `review/` / `sent/`）整体后置，研究阶段不建。
- Current artifacts: `PLAN.md`、`README.md`、`STYLE.md`、`style/target-style.json`、`style/prompt.md`、`style/new-account.json`、`scripts/collect_target.py`、`scripts/analyze_style.py`、`data/target/20261105T1052Z/`。
- Corpus (2026-11-05 capture, `data/target/20261105T1052Z/`): 164 页 / 6,539 行 / 6,217 唯一状态；本人 **3,223** 条（回复 3,034 / 原创 163 / 带 @ 缺回复元数据 26），时间 2026-10-27T14:51Z–11-05T10:16Z。资料页报告 6,611 条，观察比 **48.8%**；末页 0 行仍带 cursor，尾部另探 8 页全空——缺口在 2026-10-27 之前，属第三方接口深度上限，不是账号全量。
- **帖子语料（主对象）**：`data/target/posts-merged/posts.jsonl`，**298 条**原创帖，2026-10-20T11:15Z 至 11-06T05:05Z（17 天）。构成：镜像 293 条 + 2026-11-06 直连 `UserTweets` 抓到 335 条（转推 55 条剔除后原创 280 条），去重后净增 5 条（均 11-06）。
- **覆盖边界（已闭合）**：`UserTweets` 翻到 2026-10-10 后只剩转推、再往前是空页；Principal 在 App 手动核对「原帖确实只能看到 10-20，再早的没有了」。9-30 至 10-20 的原创帖在 X 侧不可得，官方导出是唯一补充路径；Principal 已选择不再追击（2026-11-06）。
- 采集机制备注：隐藏标签页不触发 X 分页（Chrome 节流），UI 滚动采不到；直连 GraphQL 可绕开，脚本 `scripts/collect_user_timeline.py`。`SearchTimeline` 与 `UserTweetsAndReplies` 对该只读账号返回 404，仅 `UserTweets` 可用。
- 帖子结论（`scripts/analyze_posts.py`，298 条口径）：长度中位 41 码位 / p90 80，非空行中位 3，80.2% 多行、77.2% 用空行分段，47.0% 含问号，15.8% 挂 `@grok`，24.2% 带表情（😱 为主表情），18.8% 带图；展示中位 2,784、p90 52,021、最高 209 万；日均 17 条、间隔中位约 40 分钟、高峰 17:00–22:00（UTC+8）；开头模板中「卧槽系」47 条、展示中位 5,617，是普通帖的 2.3 倍。
- 回复语料（背景，不入规范）：`data/target/20261105T1052Z/replies.jsonl` 3,034 条，中位 4 字、98.0% 无句尾标点。
- `PLAN.md` §1 仍保留 18 小时探索性抽样的数字（204 条），它们是方案阶段的临时结论；**以 `STYLE.md` 的全量数字为准**，两者差异已在 evidence 中标注。
- Decisions in force: 见 `PLAN.md` §8 与 `.agnir/decisions.md`。摘要——争议内容按对标手法复刻但每条须有来源锚点；长文整类延后；抓全量；接 Agnir；人设只做接口层。
- 接口人设（2026-11-05 定稿，`style/new-account.json`）：昵称 **ZongShi（互～）**、简介 **AI 弄潮儿**，不做固定自称（对标号无此特征）。handle 与头像由 Principal 开号时手动决定。
- 选题不受简介约束（Principal 2026-11-05 纠正）：内容对标原号，配比由 P1 从全量语料实测（样本期参考：时政/社会 39%、八卦/娱乐 28%）。
- 已知采集陷阱（来自 mt.ai 同类采集）：服务端每页约 40 行（`count=100` 也不给满）；偶发 404 需退避重试；**空页仍可能带 continuation cursor**，出现时标 `api_cursor_exhausted=false`，不得宣称"全量"。
- 未创建：新号本体、`style/new-account.json` 的最终人设、任何发送能力。

- **P2 已完成（2026-11-06）**：22 条样稿 `data/eval/20261106T-samples/samples.jsonl`，`guard/check_text.py` 0 拦截，长度分段差与四项占比差均 ≤10pp（KS 已弃用）。规则变更：原创上限 60→90 字、不写依赖配图才成立的内容、卧槽系改用当日热榜（`scripts/fetch_news.py`，头条/知乎/百度三源），正文不标来源、出处只存 `source_url`。
