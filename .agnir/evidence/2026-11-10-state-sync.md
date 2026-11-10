# 2026-11-10 线上状态同步：审稿与评分随部署包下发

- 时间：2026-11-10 17:40–18:10 (UTC+8)
- 触发：Principal 指出「评分和稿池的状态没同步到线上」——此前线上只认浏览器 localStorage，换设备就是空白。
- 产物：`site/build_dist.py`（注入 `window.__ZS_SEED__`）、`site/template.html` / `site/target_template.html`（启动时合并）、重新部署的 `https://zs.lapplax.com`

## 机制

- 构建时读取 `data/drafts/review.json` 与 `data/eval/target-ratings.json`，转成页面状态：`used` / `rejected` / `dup→duplicate`、`edited` 保留改后正文；评分直接是 `{id: score}`。
- 注入为部署包里的 `<script>window.__ZS_SEED__ = …</script>`，页面启动时只补 localStorage 里没有的 id，已有记录优先；注入后写回 localStorage，导出/复制路径不受影响。
- 正文与当前稿件一致时只存状态、不存正文，避免把没改过的稿子带进「已改」渲染分支。
- 仓库 → 线上单向；线上新标记仍需「导出」拿回仓库。

## 验证

```
python3 site/build_dist.py            # seed review=430 ratings=298
python3 -m http.server 8788 -d site/dist
Chrome --headless --dump-dom http://127.0.0.1:8788/index.html
#  c-total 554 / c-used 57 / c-rej 349 / c-dup 24 / c-pend 124 / c-shown 530
Chrome --headless --dump-dom http://127.0.0.1:8788/target.html
#  c-scored 298 / c-total 298
Chrome --headless --dump-dom https://zs.lapplax.com/
#  c-total 554 / c-used 57 / c-rej 349 / c-dup 24 / c-pend 124
Chrome --headless --dump-dom https://zs.lapplax.com/target
#  c-scored 298 / c-total 298
```

## 覆盖边界

- 只在「localStorage 无该 id 记录」时生效；之前已在线上标过的浏览器不会被仓库状态覆盖，也不会自动回收线上改动。
- 无头 Chrome 用的是一次性 profile，等价于新设备；未验证真实手机浏览器与剪贴板行为。
- 未发布、未排期、未操作账号。
