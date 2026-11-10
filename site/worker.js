/**
 * 审稿站的服务端：同一个 Worker 既出静态页，也提供 /api/state 读写 KV。
 *
 *   GET  /api/state  → { review: {id: {status?, text?}}, ratings: {id: score}, updatedAt }
 *   POST /api/state  → body 同结构；默认按 id 合并，body.replace=true 时整段覆盖
 *
 * 写入没有鉴权：站点靠 noindex 和私有 URL 隐蔽，最坏情况是被改写标记，
 * 可从 git 里的 data/drafts/review.json 与 GET 返回的副本恢复。
 */
const MAX_BODY = 2_000_000;
const JSON_HEADERS = {
  'content-type': 'application/json; charset=utf-8',
  'cache-control': 'no-store',
};

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: JSON_HEADERS });

const isPlainObject = v => v !== null && typeof v === 'object' && !Array.isArray(v);

function sanitize(doc) {
  const out = { review: {}, ratings: {} };
  for (const [id, entry] of Object.entries(doc.review || {})) {
    if (typeof id !== 'string' || !isPlainObject(entry)) continue;
    const clean = {};
    if (typeof entry.status === 'string' && entry.status.length < 24) clean.status = entry.status;
    if (typeof entry.text === 'string' && entry.text.length < 2000) clean.text = entry.text;
    if (typeof entry.image === 'string' && entry.image.length < 2000) clean.image = entry.image;
    if (Object.keys(clean).length) out.review[id] = clean;
  }
  for (const [id, score] of Object.entries(doc.ratings || {})) {
    if (typeof id === 'string' && Number.isInteger(score) && score >= 0 && score <= 10) out.ratings[id] = score;
  }
  return out;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== '/api/state') return env.ASSETS.fetch(request);
    if (!env.ZS_STATE) return json({ error: 'KV binding missing' }, 500);

    if (request.method === 'GET') {
      const raw = await env.ZS_STATE.get('doc');
      const doc = raw ? JSON.parse(raw) : { review: {}, ratings: {} };
      return json({ review: doc.review || {}, ratings: doc.ratings || {}, updatedAt: doc.updatedAt || null });
    }

    if (request.method === 'POST') {
      if (Number(request.headers.get('content-length') || 0) > MAX_BODY) {
        return json({ error: 'payload too large' }, 413);
      }
      const body = await request.json().catch(() => null);
      if (!isPlainObject(body)) return json({ error: 'invalid json' }, 400);

      const raw = await env.ZS_STATE.get('doc');
      const doc = raw ? JSON.parse(raw) : { review: {}, ratings: {} };
      const next = { review: doc.review || {}, ratings: doc.ratings || {} };
      for (const key of ['review', 'ratings']) {
        if (!(key in body)) continue;
        if (!isPlainObject(body[key])) return json({ error: `${key} must be object` }, 400);
        if (body.replace) next[key] = body[key];
        else Object.assign(next[key], body[key]);
      }
      const clean = sanitize(next);
      clean.updatedAt = new Date().toISOString();
      await env.ZS_STATE.put('doc', JSON.stringify(clean));
      return json({ ok: true, updatedAt: clean.updatedAt });
    }

    return json({ error: 'method not allowed' }, 405);
  },
};
