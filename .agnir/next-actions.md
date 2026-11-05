# Next Actions

1. **P0 全量采集**：`scripts/collect_target.py --profile-ref 'id:2105258399885844480' --output-dir data/target/<ts>`，约 165 页、1.2 s 间隔。落盘原始页、`replies.jsonl` / `originals.jsonl`、`collection.json`（页数、行数、去重数、profile 报告状态数、`termination_reason`）。验收：唯一 ID / 报告状态数 ≥ 0.95；同 ID 正文跨页一致。
2. **P1 规范**：`scripts/analyze_style.py` 在 `data/target/<ts>/` 上复算 `PLAN.md` §1 全部数字，产出 `STYLE.md` + `style/target-style.json` + `style/prompt.md`。重点复看 18 小时样本的偏差：话题配比、😱 频率、burst 结构在 36 天里是否稳定。
3. **P2 生成与自评**：`scripts/build_prompt.py` + `scripts/analyze_gap.py`，20 条样稿对语料的长度/标点/emoji/连打四项分布，KS < 0.15 才算过。
4. **接口人设定稿**（开号前，不阻塞 P0–P2）：昵称后缀「（互～）」、一句话简介、一个固定自称，写入 `style/new-account.json`；身份层禁止项写入 `guard/banned.md`。
5. **后置、需单独授权**：P3 发送与节奏、P4 增长闭环。启用前重新评估平台规则风险，并按 `PLAN.md` §5 的"后置"参数表执行。
6. 每次采集/规范变更后做 checkpoint 评估：真变了才更新本文件与 `state.md`，并在 `evidence/` 追加一条可核验记录（时间、命令、结果、覆盖边界）。
