# Next Actions

1. ~~P0 全量采集~~ 完成 2026-11-05：`data/target/20261105T1052Z/`，3,223 条本人帖，覆盖 2026-10-27 之后；48.8% 观察比，缺口与边界见 `state.md` 与 evidence。
2. ~~P1 规范~~ 完成 2026-11-05：`STYLE.md` + `style/target-style.json` + `style/prompt.md`，全部数字由 `scripts/analyze_style.py` 复算。
3. **P2 帖子生成与自评**（当前下一步）：按 `style/prompt.md` 生成 20 条帖子样稿，用 `scripts/analyze_gap.py` 对 293 条语料比对长度、非空行数、空行率、问号率、表情率，KS < 0.15 才算过。
4. **接口人设**（`style/new-account.json`）：已完成——昵称 `ZongShi（互～）`、简介 `AI 弄潮儿`，不做固定自称。handle 与头像由 Principal 在开号时手动确定，Agent 不介入。
5. **后置、需单独授权**：P3 发送与节奏、P4 增长闭环。启用前重新评估平台规则风险，并按 `PLAN.md` §5 的"后置"参数表执行。
6. 每次采集/规范变更后做 checkpoint 评估：真变了才更新本文件与 `state.md`，并在 `evidence/` 追加一条可核验记录（时间、命令、结果、覆盖边界）。
