# Current State

- Project: 复刻 X 账号 `@FKFKFKFKFKTB`（高水水（互～），数字 ID `2105258399885844480`）的文风，为一个尚未创建的新号（代号 ZongShi）产出可复算的风格规范与生成提示词。
- Authorized Project Entry Point: this repository root (`/Users/jaymini/Code/lab/xcom/ZongShi`).
- Agnir Core/profile: `1.0` / `repository-filesystem/1.0`; primary lineage: `urn:zongshi:lineage:primary`; distribution `v1.0.2` from revision `b5626394ec40a5cb7a28c01892acde07cc0adc8e`.
- **Phase: research only (Principal, 2026-11-05).** 采集、分析、规范、自评；不接账号、不发布。发送段（`send.py` / `record_sent.py` / `metrics.py` / `candidates/` / `review/` / `sent/`）整体后置，研究阶段不建。
- Current artifacts: `PLAN.md`（方案与决策记录）、`README.md`、`AGNIR.*`。`data/`、`style/`、`scripts/` 尚未创建，属 P0–P2 交付物。
- 唯一已采数据是一次**探索性抽样**（2026-11-05 手动抓取，10 页 / 414 行 / 204 条本人帖，覆盖 2026-11-04T16:42Z–11-05T10:16Z，约 18 小时），未落盘到本仓库，也未通过本仓库脚本复现。因此 `PLAN.md` §1 的所有数字是**样本结论**，不是全量结论；P0 全量采集后必须重算并以全量为准。
- 抽样期的量级（待全量复核）：目标号 6,611 条状态、6,616 粉、5,653 关注、2026-09-30 注册；样本里回复占 91.2%、回复正文中位 4 字、100% 以 `@` 开头、98.4% 无句尾标点、😱 占表情 57%，原创中位 41 字、均 13,625 浏览。
- Decisions in force: 见 `PLAN.md` §8 与 `.agnir/decisions.md`。摘要——争议内容按对标手法复刻但每条须有来源锚点；长文整类延后；抓全量；接 Agnir；人设只做接口层。
- 接口人设（2026-11-05 定稿，`style/new-account.json`）：昵称 **ZongShi（互～）**、简介 **AI 弄潮儿**；固定自称待定（候选「弄潮儿」）。话题收敛为 AI 三件（模型与工具 / 应用与产品 / 内容创作），币圈与医疗只作接话、不作原创选题。
- 已知采集陷阱（来自 mt.ai 同类采集）：服务端每页约 40 行（`count=100` 也不给满）；偶发 404 需退避重试；**空页仍可能带 continuation cursor**，出现时标 `api_cursor_exhausted=false`，不得宣称"全量"。
- 未创建：新号本体、`style/new-account.json` 的最终人设、任何发送能力。
