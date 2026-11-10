# 2026-11-10 审稿站改双向：在线标记直接落 KV，仓库 ↔ 线上可互相同步

- 时间：2026-11-10 17:40–18:25 (UTC+8)
- 触发：Principal 要求「做成双向」——此前线上只能读，改动留在浏览器里，得手动导出再放回仓库。
- 产物：`site/worker.js`（部署为 `_worker.js`）、`wrangler.toml`（KV `ZS_STATE`）、`scripts/sync_state.py`、`site/serve.py` 的 `/api/state`、两个页面的拉取/回写逻辑

## 结构

- 一个 Pages 部署同时出静态页和接口：`_worker.js` 命中 `/api/state` 时读写 KV，其余交给 `env.ASSETS`。
- 状态文档：`{review: {id: {status?, text?, image?}}, ratings: {id: score}, updatedAt}`；`POST` 默认按 id 合并，`replace: true` 整段覆盖。
- 页面：启动 `GET /api/state` 合并后再渲染，之后每次标记 `POST`（800ms 防抖）；`save()` 落 localStorage 也触发回写。启动合并期间不回写，避免把刚拉到的状态再推一遍。
- 本地：`site/serve.py` 提供同形状 `GET/POST /api/state`，直接读写仓库文件；线上「保存到仓库」按钮仍只在 localhost 出现。
- `build_dist.py` 继续注入 `window.__ZS_SEED__` 作为离线兜底（接口不可用时按仓库状态渲染）。
- 仓库 ↔ 线上：`scripts/sync_state.py pull|push|show`；pull 保留仓库原有顺序、只追加新 id，push 默认合并、`--replace` 覆盖。

## 验证（本地 pages dev + 线上）

```
GET/POST /api/state（wrangler pages dev 8789）
# 空 KV → 页面加载后把自己 430 条审稿、298 条评分推上去
# 改动 p100 为 used → 新 profile 打开页面：used 58，p100 标签「已用」
# CDP 点击 p099「重复」→ KV 里 p099 = duplicate
# target 页：scored 298，KV ratings 298（均分 4.20）
线上 https://zs.lapplax.com
# 新 profile：554 条、57 已用 / 24 重复 / 349 废弃；target 298/298
# CDP 点 p098「重复」→ GET /api/state 出现 p098: duplicate，随后 push --replace 还原
# 线上把 2112503029052346548 改成 9 → target 页该卡显示「9 分」；CDP 点 7 → API 记 7，再还原
python3 scripts/sync_state.py pull   # 430/298，文件无 diff（幂等）
```

## 覆盖边界与风险

- `/api/state` 无鉴权：知道 URL 的人可以改写标记。最坏情况是状态被刷，`push --replace` 可从仓库恢复；页面只把文本写进 `textContent`，没有注入面。
- KV 里可能残留未知 id（如 `preview-test`），写入时已按稿件/对标 id 过滤，页面渲染时也会忽略。
- 预览分支与生产共用同一个 KV（`wrangler.toml` 里绑的是同一个命名空间）。
- 未验证：真实手机浏览器、弱网下的并发同步、多人同时编辑的冲突（当前策略是后写覆盖）。
- 未发布、未排期、未操作账号。
