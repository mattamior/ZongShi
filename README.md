# ZongShi — 对标 @FKFKFKFKFKTB 的账号风格复刻（研究阶段）

本仓库研究 X 账号 [@FKFKFKFKFKTB](https://x.com/FKFKFKFKFKTB)（高水水（互～））的发布与回复文风，产出可复算的风格规范与生成提示词。实现路径参考 `~/Code/lab/mt.ai`（`@mattamior` 的采集 → 规范 → 检索增强生成 → 发送闭环），但**当前只做研究段**：采集、分析、规范、自评；不接账号、不发布。

## 当前产物

- [PLAN.md](PLAN.md)：方案主体。目标账号风格实测（§1）、复刻边界（§2）、架构（§3）、分阶段（§4）、参数（§5）、验收（§6）、风险（§7）、决策记录（§8）。
- [STYLE.md](STYLE.md)：全量语料的风格结论——覆盖 2026-10-27 至 11-05，3,223 条本人帖（回复 3,034 / 原创 163）。
- [style/target-style.json](style/target-style.json)：机器可读规范（硬规则、语域菜单、真实例句、指标、题材配比）。
- [style/prompt.md](style/prompt.md)：可直接复制的提示词（回复 + 原创）。
- [style/new-account.json](style/new-account.json)：新号接口人设（ZongShi（互～）/ AI 弄潮儿）。
- [data/target/20261105T1052Z/](data/target/20261105T1052Z/)：原始页 + `authored/replies/originals.jsonl` + `collection.json` + `style-stats.json`。
- 统计复算：`python3 scripts/analyze_style.py data/target/20261105T1052Z`。

## 已定边界（摘要）

- 争议内容按对标账号的**处理手法**复刻（提问包装 / 反差并置 / 骂公敌 / 热搜跟评），不按它的**具体断言**复刻；无来源的争议帖只写提问，不写事实。
- 长文体裁（"14 天上岸"复盘）整类延后，等本号自己跑出数据再解禁。
- 人设只做接口层（昵称、简介、固定自称），不做身份层（学历、战绩、机构）。
- 发送段（`send.py` / `record_sent.py` / `metrics.py`）后置，研究阶段不建。

## Agnir Project Instructions

本项目的规范激活与操作说明位于 [AGNIR.md](AGNIR.md)。本节仅作为向后兼容的定位入口。
