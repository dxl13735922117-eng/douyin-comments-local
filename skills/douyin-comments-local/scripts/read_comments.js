// SPDX-License-Identifier: MIT
// Function expression for a documented read-only DOM evaluation surface.
(options) => {
  const cfg = Object.assign({
    root: '[data-e2e="comment-list"]',
    top: '[data-e2e="comment-item"]',
    body: '.FduGc_lz > .Sh1Da424',
    author: '.comment-item-info-wrap a',
    likes: '.VpA2NKl1',
    time: '.VAQA49VP',
    id_node: '[data-e2e="video-comment-more"] [id^="tooltip_"]',
    id_attribute: 'id',
    id_prefix: 'tooltip_',
    counter: '[data-e2e="feed-comment-icon"]',
    offset: 0,
    limit: 30
  }, options || {});
  if (!/^\d+$/.test(String(cfg.video_id || ''))) {
    throw new Error('Pass the video_id verified from the current page URL.');
  }
  const roots = Array.from(document.querySelectorAll(cfg.root));
  if (roots.length !== 1) throw new Error('Expected exactly one observed comment root.');
  const root = roots[0];
  const visible = el => !!(el && !el.closest('[hidden], [aria-hidden="true"]') &&
    (el.getClientRects().length || Array.from(el.querySelectorAll('*')).some(child => child.getClientRects().length)));
  const text = el => {
    if (!visible(el)) return '';
    const visit = node => {
      if (node.nodeType === 3) return node.textContent;
      if (node.nodeType !== 1) return '';
      if (node.hasAttribute('hidden') || node.getAttribute('aria-hidden') === 'true') return '';
      if (node.tagName === 'IMG') return node.getAttribute('alt') || '';
      if (node.tagName === 'BR') return '\n';
      return Array.from(node.childNodes).map(visit).join('');
    };
    return visit(el).trim();
  };
  const field = (el, selector) => selector ? text(el.querySelector(selector)) : '';
  const id = el => {
    if (!el) return '';
    const node = cfg.id_node ? el.querySelector(cfg.id_node) : el;
    let value = node && cfg.id_attribute ? node.getAttribute(cfg.id_attribute) || '' : '';
    if (cfg.id_prefix) {
      if (!value.startsWith(cfg.id_prefix)) return '';
      value = value.slice(cfg.id_prefix.length);
    }
    return value;
  };
  const record = el => {
    const body = el.querySelector(cfg.body);
    if (!visible(body) || !text(body)) throw new Error('A rendered comment has no readable body; inspect selectors before continuing.');
    if (body.querySelector(cfg.top)) throw new Error('Body includes nested comments; narrow the body selector.');
    return {cid:id(el),author:field(el,cfg.author),text:text(body),
      likes_text:field(el,cfg.likes),time_text:field(el,cfg.time)};
  };
  const all = Array.from(root.querySelectorAll(cfg.top)).filter(visible);
  const tops = all.filter(el => !el.parentElement.closest(cfg.top));
  if (!tops.length) throw new Error('No rendered comment items matched; this is not evidence of zero comments.');
  const offset = Math.max(0, Math.floor(Number(cfg.offset) || 0));
  const limit = Math.min(100, Math.max(1, Math.floor(Number(cfg.limit) || 30)));
  const comments = tops.slice(offset,offset+limit).map(el => ({
    ...record(el),
    replies:Array.from(el.querySelectorAll(cfg.top))
      .filter(reply => visible(reply) && reply.parentElement.closest(cfg.top) === el)
      .map(record)
  }));
  const controls = Array.from(root.querySelectorAll('button')).filter(el => visible(el) && /^(展开|更多回复)/.test(text(el)));
  return {schema:'dyc-dom-v1',mode:'browser-ui',video_id:String(cfg.video_id),
    title:document.title,comments,matched_top_nodes:tops.length,
    next_offset:Math.min(offset+limit,tops.length),has_more:offset+limit<tops.length,
    unexpanded:controls.map(el => ({parent_cid:id(el.closest(cfg.top)),text:text(el)})),
    page_count_text:field(document,cfg.counter),
    bottom_excerpt:(root.innerText || '').slice(-180)};
}
