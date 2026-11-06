# ZongShi — 对标 @FKFKFKFKFKTB 的账号风格复刻（研究阶段）

本仓库研究 X 账号 [@FKFKFKFKFKTB](https://x.com/FKFKFKFKFKTB)（高水水（互～））的**发帖**风格，产出可复算的规范与生成提示词。回复不进入规范。实现路径参考 `~/Code/lab/mt.ai`（`@mattamior` 的采集 → 规范 → 检索增强生成 → 发送闭环），但**当前只做研究段**：采集、分析、规范、自评；不接账号、不发布。

## 当前产物

- [PLAN.md](PLAN.md)：方案主体。目标账号风格实测（§1）、复刻边界（§2）、架构（§3）、分阶段（§4）、参数（§5）、验收（§6）、风险（§7）、决策记录（§8）。
- [STYLE.md](STYLE.md)：帖子风格结论——293 条原创帖，2026-10-20 至 11-05。
- [style/target-style.json](style/target-style.json)：机器可读规范（硬规则、语域菜单、真实例句、指标、题材配比）。
- [style/prompt.md](style/prompt.md)：可直接复制的提示词（回复 + 原创）。
- [style/new-account.json](style/new-account.json)：新号接口人设（ZongShi（互～）/ AI 弄潮儿）。
- [data/target/posts-merged/posts.jsonl](data/target/posts-merged/posts.jsonl)：合并后的 293 条原创帖（去重），含 `post-stats.json`。
- [data/target/20261105T-posts/](data/target/20261105T-posts/)：纯帖子路由原始页（278 条，2026-10-20 起）。
- [data/target/20261105T1052Z/](data/target/20261105T1052Z/)：回复路由全量抓取，用于补齐 10-27 之后的原创与背景。
- 统计复算：`python3 scripts/analyze_posts.py data/target/posts-merged/posts.jsonl`。

## 已定边界（摘要）

- 争议内容按对标账号的**处理手法**复刻（提问包装 / 反差并置 / 骂公敌 / 热搜跟评），不按它的**具体断言**复刻；无来源的争议帖只写提问，不写事实。
- 长文体裁（"14 天上岸"复盘）整类延后，等本号自己跑出数据再解禁。
- 人设只做接口层（昵称、简介、固定自称），不做身份层（学历、战绩、机构）。
- 发送段（`send.py` / `record_sent.py` / `metrics.py`）后置，研究阶段不建。

## Agnir Project Instructions

本项目的规范激活与操作说明位于 [AGNIR.md](AGNIR.md)。本节仅作为向后兼容的定位入口。
