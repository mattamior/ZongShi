# Current State

- Project: 复刻 X 账号 `@FKFKFKFKFKTB`（高水水（互～），数字 ID `2105258399885844480`）的文风，为一个尚未创建的新号（代号 ZongShi）产出可复算的风格规范与生成提示词。
- Authorized Project Entry Point: this repository root (`/Users/jaymini/Code/lab/xcom/ZongShi`).
- Agnir Core/profile: `1.0` / `repository-filesystem/1.0`; primary lineage: `urn:zongshi:lineage:primary`; distribution `v1.0.2` from revision `b5626394ec40a5cb7a28c01892acde07cc0adc8e`.
- **Phase: research only (Principal, 2026-11-05).** 采集、分析、规范、自评；不接账号、不发布。发送段（`send.py` / `record_sent.py` / `metrics.py` / `candidates/` / `review/` / `sent/`）整体后置，研究阶段不建。
- Current artifacts: `PLAN.md`、`README.md`、`STYLE.md`、`style/target-style.json`、`style/prompt.md`、`style/new-account.json`、`scripts/collect_target.py`、`scripts/analyze_style.py`、`data/target/20261105T1052Z/`。
- Corpus (2026-11-05 capture, `data/target/20261105T1052Z/`): 164 页 / 6,539 行 / 6,217 唯一状态；本人 **3,223** 条（回复 3,034 / 原创 163 / 带 @ 缺回复元数据 26），时间 2026-10-27T14:51Z–11-05T10:16Z。资料页报告 6,611 条，观察比 **48.8%**；末页 0 行仍带 cursor，尾部另探 8 页全空——缺口在 2026-10-27 之前，属第三方接口深度上限，不是账号全量。
- 风格结论（全量复算）：回复 99.93% 以 @ 开头、正文中位 4 码位 / p90 10、98.0% 无句尾标点、15.4% 带表情（😱 286 为首）、纯表情 9.0%、14 字以上极少；原创 163 条中位 41 码位、5 行、77.9% 多行、44.8% 含问号、18.4% 挂 @grok；节奏 15.2 条/小时、间隔中位 29 秒。
- `PLAN.md` §1 仍保留 18 小时探索性抽样的数字（204 条），它们是方案阶段的临时结论；**以 `STYLE.md` 的全量数字为准**，两者差异已在 evidence 中标注。
- Decisions in force: 见 `PLAN.md` §8 与 `.agnir/decisions.md`。摘要——争议内容按对标手法复刻但每条须有来源锚点；长文整类延后；抓全量；接 Agnir；人设只做接口层。
- 接口人设（2026-11-05 定稿，`style/new-account.json`）：昵称 **ZongShi（互～）**、简介 **AI 弄潮儿**，不做固定自称（对标号无此特征）。handle 与头像由 Principal 开号时手动决定。
- 选题不受简介约束（Principal 2026-11-05 纠正）：内容对标原号，配比由 P1 从全量语料实测（样本期参考：时政/社会 39%、八卦/娱乐 28%）。
- 已知采集陷阱（来自 mt.ai 同类采集）：服务端每页约 40 行（`count=100` 也不给满）；偶发 404 需退避重试；**空页仍可能带 continuation cursor**，出现时标 `api_cursor_exhausted=false`，不得宣称"全量"。
- 未创建：新号本体、`style/new-account.json` 的最终人设、任何发送能力。
